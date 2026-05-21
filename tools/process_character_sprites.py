#!/usr/bin/env python3
"""Process AI-generated character sprite sources into game-ready sprite sheets.

A standalone CLI tool that reads a simple JSON config per character and
produces properly scaled, anchored, horizontal sprite sheets.

Usage:
    # Process one character
    python tools/process_character_sprites.py tools/sprite_defs/characters/ramon.json

    # Process multiple characters
    python tools/process_character_sprites.py tools/sprite_defs/characters/*.json

    # Verbose mode (shows per-frame crop/scale details)
    python tools/process_character_sprites.py -v tools/sprite_defs/characters/ramon.json

Config format (JSON):
    {
      "frame_width": 48,
      "frame_height": 64,
      "source_dir": "assets/ai_sources/ramon",
      "output_dir": "assets/sprites/ramon",
      "animations": [
        {"source": "idle.png", "frames": 4, "anchor": "ground"},
        {"source": "walk.png", "frames": 6, "anchor": "ground"},
        {"source": "jump.png", "frames": 2, "anchor": "center"},
        {"source": "death.png", "frames": 1, "anchor": "center", "independent_scale": true}
      ]
    }

Scaling rules:
    - Body-height normalization: idle is the reference height.  Ground-anchored
      animations that are shorter than idle get pre-scaled UP so the character
      stays the same height (AI sources draw inconsistent sizes).  Taller
      animations keep their natural size.  Set "normalize": false to opt out
      (e.g. crouch).
    - One shared scale factor is then computed from the pre-scaled global max
      to fit the frame.  Final scale = pre_scale * shared_scale.
    - Animations with "independent_scale": true get their own scale.

Anchor modes:
    - "ground": center horizontally, bottom-align (feet on floor)
    - "center": center both horizontally and vertically (airborne/death)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy import ndimage

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Green chroma-key removal
# ---------------------------------------------------------------------------

def remove_green_background(arr: np.ndarray) -> np.ndarray:
    """Remove green chroma-key background and return RGBA array.

    Green pixels are detected where g-r > 40, g-b > 40, and g > 80.

    Args:
        arr: Input image as numpy array (H, W, 3 or 4).

    Returns:
        RGBA numpy array with green pixels made transparent.
    """
    rgb = arr[:, :, :3]
    r = rgb[:, :, 0].astype(np.int32)
    g = rgb[:, :, 1].astype(np.int32)
    b = rgb[:, :, 2].astype(np.int32)

    is_green = (g - r > 40) & (g - b > 40) & (rgb[:, :, 1] > 80)

    rgba = np.zeros((*arr.shape[:2], 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = np.where(is_green, 0, 255)

    return rgba


# ---------------------------------------------------------------------------
# Small component removal
# ---------------------------------------------------------------------------

def remove_small_components(
    rgba: np.ndarray,
    min_area: int = 5000,
) -> np.ndarray:
    """Remove small connected components (labels/artifacts) from RGBA image.

    Makes components below min_area fully transparent so they don't
    interfere with bounding box detection.

    Args:
        rgba: RGBA image array.
        min_area: Components below this pixel area become transparent.

    Returns:
        Cleaned RGBA array.
    """
    mask = rgba[:, :, 3] > 0
    labeled, n_features = ndimage.label(mask)

    cleaned = rgba.copy()
    for region_id in range(1, n_features + 1):
        region_mask = labeled == region_id
        area = int(np.sum(region_mask))
        if area < min_area:
            cleaned[region_mask, 3] = 0

    return cleaned


# ---------------------------------------------------------------------------
# Region detection and cropping
# ---------------------------------------------------------------------------

def detect_sprite_regions(
    rgba: np.ndarray,
    min_area: int = 5000,
) -> list[tuple[int, int, int, int]]:
    """Detect sprite regions via connected-component labeling.

    Args:
        rgba: RGBA image array with small components already removed.
        min_area: Minimum pixel area for a region.

    Returns:
        List of (x0, y0, x1, y1) bounding boxes, sorted left-to-right.
    """
    mask = rgba[:, :, 3] > 0
    labeled, n_features = ndimage.label(mask)

    regions: list[tuple[int, int, int, int, int]] = []
    for region_id in range(1, n_features + 1):
        ys, xs = np.where(labeled == region_id)
        area = len(ys)
        if area < min_area:
            continue
        x0 = int(xs.min())
        x1 = int(xs.max()) + 1
        y0 = int(ys.min())
        y1 = int(ys.max()) + 1
        regions.append((x0, y0, x1, y1, area))

    regions.sort(key=lambda r: r[0])
    return [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in regions]


def crop_region(rgba: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """Crop a region and tight-crop to non-transparent content.

    Args:
        rgba: Full RGBA image array.
        bbox: (x0, y0, x1, y1) bounding box.

    Returns:
        Tightly cropped RGBA array.
    """
    x0, y0, x1, y1 = bbox
    crop = rgba[y0:y1, x0:x1].copy()

    alpha = crop[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)

    if not np.any(rows):
        return crop

    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]

    return crop[r0:r1 + 1, c0:c1 + 1]


# ---------------------------------------------------------------------------
# Green fringe cleaning
# ---------------------------------------------------------------------------

def clean_green_fringe(crop: np.ndarray) -> np.ndarray:
    """Remove green fringe pixels via neighbor averaging.

    After chroma removal, edge pixels may retain green tint. This
    replaces them with the average of non-green neighbors.

    Args:
        crop: Cropped RGBA numpy array.

    Returns:
        Cleaned RGBA array.
    """
    result = crop.copy()
    r = result[:, :, 0].astype(np.int32)
    g = result[:, :, 1].astype(np.int32)
    b = result[:, :, 2].astype(np.int32)
    a = result[:, :, 3]

    green_mask = (g - r > 30) & (g - b > 30) & (g > 100) & (a > 0)

    if not np.any(green_mask):
        return result

    h, w = result.shape[:2]
    gy, gx = np.where(green_mask)

    for cy, cx in zip(gy, gx):
        neighbors = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if not green_mask[ny, nx] and result[ny, nx, 3] > 0:
                        neighbors.append(result[ny, nx, :3].astype(np.float32))
        if neighbors:
            avg = np.mean(neighbors, axis=0).astype(np.uint8)
            result[cy, cx, :3] = avg
        else:
            result[cy, cx, 3] = 0

    return result


# ---------------------------------------------------------------------------
# Scaling and placement
# ---------------------------------------------------------------------------

def scale_sprite(sprite: np.ndarray, scale: float) -> np.ndarray:
    """Scale a sprite by the given factor using LANCZOS interpolation.

    Args:
        sprite: Tightly cropped RGBA array.
        scale: Scale factor to apply.

    Returns:
        Scaled RGBA array.
    """
    if sprite.size == 0:
        return sprite

    sh, sw = sprite.shape[:2]
    new_w = max(1, int(sw * scale))
    new_h = max(1, int(sh * scale))

    pil = Image.fromarray(sprite, "RGBA")
    pil_scaled = pil.resize((new_w, new_h), Image.LANCZOS)
    return np.array(pil_scaled)


def place_in_frame(
    scaled: np.ndarray,
    frame_w: int,
    frame_h: int,
    anchor: str = "ground",
) -> np.ndarray:
    """Place a scaled sprite into a fixed-size frame.

    If the scaled sprite overflows the frame, it is clipped (not rescaled)
    to preserve the uniform scale factor.

    Args:
        scaled: Scaled RGBA sprite array.
        frame_w: Target frame width.
        frame_h: Target frame height.
        anchor: "ground" for bottom-aligned or "center" for vertically
            centered placement.

    Returns:
        RGBA array of exactly (frame_h, frame_w, 4).
    """
    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    if scaled.size == 0:
        return frame

    ph, pw = scaled.shape[:2]

    # Clip if sprite overflows frame
    if ph > frame_h:
        if anchor == "center":
            # Center-clip vertically
            top_clip = (ph - frame_h) // 2
            scaled = scaled[top_clip:top_clip + frame_h]
        else:
            # Bottom-clip for ground anchor (keep feet, clip head)
            scaled = scaled[ph - frame_h:]
        ph = frame_h

    if pw > frame_w:
        # Center-clip horizontally
        left_clip = (pw - frame_w) // 2
        scaled = scaled[:, left_clip:left_clip + frame_w]
        pw = frame_w

    # Horizontal: always center
    x_offset = (frame_w - pw) // 2

    # Vertical: depends on anchor
    if anchor == "center":
        y_offset = (frame_h - ph) // 2
    else:
        # "ground" — bottom-aligned (feet on ground line)
        y_offset = frame_h - ph

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = scaled
    return frame


# ---------------------------------------------------------------------------
# Sprite sheet assembly and saving
# ---------------------------------------------------------------------------

def assemble_sheet(frames: list[np.ndarray]) -> np.ndarray:
    """Assemble frames into a horizontal sprite sheet.

    Args:
        frames: List of same-sized RGBA arrays.

    Returns:
        RGBA array with frames laid out horizontally.
    """
    if not frames:
        return np.zeros((1, 1, 4), dtype=np.uint8)

    h, w = frames[0].shape[:2]
    sheet = np.zeros((h, w * len(frames), 4), dtype=np.uint8)
    for i, frame in enumerate(frames):
        sheet[:, i * w:(i + 1) * w] = frame
    return sheet


def save_sheet(sheet: np.ndarray, path: Path) -> None:
    """Save an RGBA sheet as PNG.

    Args:
        sheet: RGBA numpy array.
        path: Output file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(sheet, "RGBA")
    img.save(str(path))
    try:
        display_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = path
    log.info("Saved: %s (%dx%d)", display_path, sheet.shape[1], sheet.shape[0])


# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------

def process_character(config_path: Path) -> tuple[int, int]:
    """Process all animations for one character from a JSON config file.

    Processing steps:
    1. Load each source image, remove green background, remove small
       components (<5000px), detect sprite regions, crop each frame,
       and clean green fringe.
    2. Body-height normalization: find the idle animation's max crop
       height as reference.  Ground-anchored animations that are shorter
       get a pre-scale factor to match idle height (AI sources draw
       animations at inconsistent sizes).  Taller animations and
       center-anchored animations keep pre_scale 1.0.  Set
       "normalize": false in the config to opt out (e.g. crouch).
    3. Compute global max dimensions from all pre-scaled shared-scale
       crops, then ONE shared scale factor to fit the frame.
    4. Final scale per animation = pre_scale * shared_scale.
    5. For independent_scale animations: own scale from own dimensions.
    6. Place each scaled frame using anchor: "ground" = bottom-aligned,
       "center" = vertically centered.
    7. If a scaled frame overflows, clip (don't rescale).
    8. Assemble frames into horizontal sprite sheet and save as PNG.

    Args:
        config_path: Path to character JSON config file.

    Returns:
        Tuple of (successes, failures).
    """
    with open(config_path) as f:
        config = json.load(f)

    frame_w: int = config["frame_width"]
    frame_h: int = config["frame_height"]
    source_dir = PROJECT_ROOT / config["source_dir"]
    output_dir = PROJECT_ROOT / config["output_dir"]
    anim_entries: list[dict[str, Any]] = config["animations"]

    log.info("Character: %s", config_path.stem)
    log.info("  Source: %s", source_dir)
    log.info("  Output: %s", output_dir)
    log.info("  Frame: %dx%d", frame_w, frame_h)
    log.info("  Animations: %d", len(anim_entries))

    # ------------------------------------------------------------------
    # Step 1: Load, chroma-remove, detect, crop all animations
    # ------------------------------------------------------------------
    animations: list[dict[str, Any]] = []
    failures = 0

    for entry in anim_entries:
        source_path = source_dir / entry["source"]
        output_name = entry.get("output", entry["source"])
        output_path = output_dir / output_name
        expected_frames: int = entry["frames"]
        anchor: str = entry.get("anchor", "ground")
        independent: bool = entry.get("independent_scale", False)

        if not source_path.exists():
            log.error("Source not found: %s", source_path)
            failures += 1
            continue

        log.info(
            "  Loading: %s (%d frames, anchor=%s%s)",
            source_path.name, expected_frames, anchor,
            ", independent" if independent else "",
        )

        img = np.array(Image.open(source_path))
        rgba = remove_green_background(img)
        cleaned = remove_small_components(rgba, min_area=5000)

        bboxes = detect_sprite_regions(cleaned, min_area=5000)

        log.debug("    Detected %d sprite regions", len(bboxes))

        if len(bboxes) == 0:
            log.error("    No sprite regions found in %s", source_path.name)
            failures += 1
            continue

        frame_count = min(len(bboxes), expected_frames)

        cropped_frames: list[np.ndarray] = []
        for i in range(frame_count):
            cropped = crop_region(cleaned, bboxes[i])
            cropped = clean_green_fringe(cropped)
            cropped_frames.append(cropped)

        # Duplicate last frame if fewer found than expected
        while len(cropped_frames) < expected_frames:
            log.debug(
                "    Duplicating last frame (%d found, %d expected)",
                frame_count, expected_frames,
            )
            cropped_frames.append(cropped_frames[-1].copy())

        animations.append({
            "entry": entry,
            "output_path": output_path,
            "anchor": anchor,
            "independent_scale": independent,
            "cropped_frames": cropped_frames,
        })

    # ------------------------------------------------------------------
    # Step 2: Body-height normalization
    #
    # AI sources draw animations at inconsistent sizes.  Use idle as
    # the reference: ground-anchored animations that are SHORTER than
    # idle get a pre_scale to match idle height.  Taller animations,
    # center-anchored animations, and those with normalize:false keep
    # pre_scale = 1.0.
    # ------------------------------------------------------------------
    reference_h = 0.0
    for anim in animations:
        if anim["independent_scale"]:
            continue
        src = anim["entry"]["source"].lower()
        if "idle" in src:
            reference_h = max(
                float(c.shape[0]) for c in anim["cropped_frames"]
            )
            break

    if reference_h == 0.0:
        for anim in animations:
            if not anim["independent_scale"] and anim["anchor"] == "ground":
                reference_h = max(
                    float(c.shape[0]) for c in anim["cropped_frames"]
                )
                break

    log.info("  Reference height (idle): %.0f px", reference_h)

    for anim in animations:
        if anim["independent_scale"]:
            anim["pre_scale"] = 1.0
            continue

        normalize = anim["entry"].get("normalize", True)
        max_h = max(float(c.shape[0]) for c in anim["cropped_frames"])

        if (
            anim["anchor"] == "ground"
            and normalize
            and reference_h > 0
            and max_h < reference_h
        ):
            anim["pre_scale"] = reference_h / max_h
            log.info(
                "    %s: pre_scale %.3f (crop %dpx -> %dpx to match idle)",
                anim["entry"]["source"], anim["pre_scale"],
                int(max_h), int(reference_h),
            )
        else:
            anim["pre_scale"] = 1.0

    # ------------------------------------------------------------------
    # Step 3: Compute shared scale from pre-scaled global max
    # ------------------------------------------------------------------
    global_max_w = 0.0
    global_max_h = 0.0
    for anim in animations:
        if anim["independent_scale"]:
            continue
        ps = anim["pre_scale"]
        for crop in anim["cropped_frames"]:
            global_max_w = max(global_max_w, float(crop.shape[1]) * ps)
            global_max_h = max(global_max_h, float(crop.shape[0]) * ps)

    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)

    if global_max_w > 0 and global_max_h > 0:
        shared_scale = min(usable_w / global_max_w, usable_h / global_max_h)
    else:
        shared_scale = 1.0

    log.info(
        "  Shared scale: %.4f (pre-scaled max %.0fx%.0f -> %dx%d frame)",
        shared_scale, global_max_w, global_max_h, frame_w, frame_h,
    )

    # ------------------------------------------------------------------
    # Step 4: Scale, place, assemble, and save each animation
    # ------------------------------------------------------------------
    successes = 0

    for anim in animations:
        entry = anim["entry"]
        output_path: Path = anim["output_path"]
        anchor: str = anim["anchor"]
        independent: bool = anim["independent_scale"]
        cropped_frames: list[np.ndarray] = anim["cropped_frames"]

        if independent:
            own_max_w = max(c.shape[1] for c in cropped_frames)
            own_max_h = max(c.shape[0] for c in cropped_frames)
            scale = min(usable_w / own_max_w, usable_h / own_max_h)
            log.debug(
                "  %s: independent scale %.4f (max %dx%d)",
                output_path.name, scale, own_max_w, own_max_h,
            )
        else:
            scale = anim["pre_scale"] * shared_scale

        frames: list[np.ndarray] = []
        for i, cropped in enumerate(cropped_frames):
            scaled = scale_sprite(cropped, scale)
            placed = place_in_frame(scaled, frame_w, frame_h, anchor)
            frames.append(placed)
            log.debug(
                "    Frame %d: %dx%d -> %dx%d in %dx%d (scale=%.4f)",
                i + 1, cropped.shape[1], cropped.shape[0],
                scaled.shape[1], scaled.shape[0],
                frame_w, frame_h, scale,
            )

        sheet = assemble_sheet(frames)
        save_sheet(sheet, output_path)
        successes += 1

    return successes, failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Process AI-generated sprite sources into game-ready sprite sheets."
        ),
    )
    parser.add_argument(
        "config",
        nargs="+",
        help="Path(s) to character JSON config files",
    )
    parser.add_argument(
        "-v",
        action="store_true",
        dest="verbose",
        help="Enable verbose logging",
    )
    return parser


def main() -> None:
    """Entry point: parse args and process each config."""
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    total_successes = 0
    total_failures = 0

    for config_file in args.config:
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = PROJECT_ROOT / config_path

        if not config_path.exists():
            log.error("Config not found: %s", config_path)
            total_failures += 1
            continue

        successes, failures = process_character(config_path)
        total_successes += successes
        total_failures += failures
        log.info("")

    log.info("Done: %d animations saved, %d failures", total_successes, total_failures)

    if total_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
