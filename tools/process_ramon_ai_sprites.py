"""Process AI-generated Ramon sprite sheets into game-ready sprite sheets.

Takes individual AI source images from assets/ai_sources/ramon/ (one per
animation) with green backgrounds and number labels, and produces
horizontal sprite sheets at pixel-art resolution in assets/sprites/ramon/.

Processing pipeline:
1. Chroma key removal  -- green background to transparent
2. Connected component labeling -- detect all non-transparent regions
3. Label/artifact removal -- filter out small components (number labels,
   stray pixels) by area threshold
4. Frame sorting -- sort remaining sprite regions left-to-right
5. Crop and scale -- crop each frame bbox, scale to target frame size
   using LANCZOS interpolation for smooth downscaling
6. Frame placement -- center horizontally, bottom-align (feet anchored)
   in target frame; death pose is vertically centered instead
7. Assembly -- combine frames into a single horizontal sprite sheet
8. Save -- output to assets/sprites/ramon/

Reusable for other characters: accepts source_dir, output_dir, frame_size,
and a mapping of source->target filenames with expected frame counts.

Usage:
    conda activate safona
    python tools/process_ramon_ai_sprites.py
    python tools/process_ramon_ai_sprites.py --source-dir assets/ai_sources/ramon \\
        --output-dir assets/sprites/ramon --frame-width 24 --frame-height 32
"""

from __future__ import annotations

import argparse
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

# Default mapping: source filename -> (target filename, expected frame count)
RAMON_MAPPING: list[dict[str, Any]] = [
    {"source": "idle.png", "target": "idle.png", "frames": 4},
    {"source": "walk.png", "target": "walk.png", "frames": 6},
    {"source": "jump.png", "target": "jump.png", "frames": 2},
    {"source": "wall_slide.png", "target": "wall_slide.png", "frames": 2},
    {"source": "wall_jump.png", "target": "wall_jump.png", "frames": 2},
    {"source": "sling_attack.png", "target": "sling.png", "frames": 3},
    {"source": "hit.png", "target": "hit.png", "frames": 1},
    {"source": "death.png", "target": "death.png", "frames": 1},
]


# ---------------------------------------------------------------------------
# Chroma key removal
# ---------------------------------------------------------------------------

def remove_green_background(arr: np.ndarray) -> np.ndarray:
    """Remove green chroma-key background and return RGBA array.

    Uses a heuristic that detects green-dominant pixels: the green
    channel must exceed both red and blue by a margin, and the green
    value must be above a minimum threshold.

    Args:
        arr: Input image as numpy array (H, W, 3 or 4).

    Returns:
        RGBA numpy array with green pixels made transparent.
    """
    rgb = arr[:, :, :3]
    r = rgb[:, :, 0].astype(np.int32)
    g = rgb[:, :, 1].astype(np.int32)
    b = rgb[:, :, 2].astype(np.int32)

    # Green pixels: G dominates R and B, and G is above minimum
    is_green = (g > 80) & (g - r > 40) & (g - b > 40)

    rgba = np.zeros((*arr.shape[:2], 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = np.where(is_green, 0, 255)

    return rgba


# ---------------------------------------------------------------------------
# Connected component detection and filtering
# ---------------------------------------------------------------------------

def detect_sprite_regions(
    rgba: np.ndarray,
    min_area: int = 5000,
) -> list[tuple[int, int, int, int]]:
    """Detect sprite frame regions, filtering out small artifacts and labels.

    Uses scipy connected component labeling on the alpha channel to find
    all non-transparent regions. Components below min_area are discarded
    (these are number labels, stray pixels, and other artifacts from the
    AI generation). Remaining regions are sorted left-to-right.

    Args:
        rgba: RGBA image array with green background removed.
        min_area: Minimum pixel area for a region to be kept as a
            sprite frame. AI number labels are typically < 2000px,
            while actual sprite frames are > 25000px.

    Returns:
        List of (x0, y0, x1, y1) bounding boxes sorted left-to-right.
    """
    mask = rgba[:, :, 3] > 0
    labeled, n_features = ndimage.label(mask)

    regions: list[tuple[int, int, int, int, int]] = []
    for region_id in range(1, n_features + 1):
        ys, xs = np.where(labeled == region_id)
        area = len(ys)
        if area < min_area:
            log.debug(
                "  Discarded component %d (area=%d) -- likely label/artifact",
                region_id, area,
            )
            continue
        x0 = int(xs.min())
        x1 = int(xs.max()) + 1
        y0 = int(ys.min())
        y1 = int(ys.max()) + 1
        regions.append((x0, y0, x1, y1, area))

    # Sort left-to-right by x0
    regions.sort(key=lambda r: r[0])

    log.info(
        "  Detected %d sprite regions (filtered %d small components)",
        len(regions), n_features - len(regions),
    )
    for i, (x0, y0, x1, y1, area) in enumerate(regions):
        log.info(
            "    Region %d: bbox=(%d,%d)-(%d,%d) w=%d h=%d area=%d",
            i + 1, x0, y0, x1, y1, x1 - x0, y1 - y0, area,
        )

    return [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in regions]


# ---------------------------------------------------------------------------
# Remove small artifacts from the RGBA image directly
# ---------------------------------------------------------------------------

def remove_small_components(
    rgba: np.ndarray,
    min_area: int = 5000,
) -> np.ndarray:
    """Remove small connected components from the RGBA image.

    Makes small components (number labels, artifacts) fully transparent
    so they don't interfere with bounding box cropping.

    Args:
        rgba: RGBA image array.
        min_area: Components with area below this become transparent.

    Returns:
        Cleaned RGBA array with small components removed.
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
# Crop, scale, and frame a single sprite
# ---------------------------------------------------------------------------

def crop_region(rgba: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """Crop a region from the image and tight-crop to content.

    Args:
        rgba: Full RGBA image array.
        bbox: (x0, y0, x1, y1) bounding box.

    Returns:
        Tightly cropped RGBA array containing only non-transparent pixels.
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


def clean_green_fringe(crop: np.ndarray) -> np.ndarray:
    """Remove remaining green fringe pixels from a cropped sprite.

    After chroma key removal, edge pixels may retain a green tint.
    This replaces them with the average color of their non-green
    neighbors, or makes them transparent if no valid neighbors exist.

    Args:
        crop: Cropped RGBA numpy array.

    Returns:
        Cleaned RGBA array with green fringe removed.
    """
    result = crop.copy()
    r = result[:, :, 0].astype(np.int32)
    g = result[:, :, 1].astype(np.int32)
    b = result[:, :, 2].astype(np.int32)
    a = result[:, :, 3]

    # Relaxed green detection for fringe pixels
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


def scale_to_frame(
    sprite: np.ndarray,
    frame_w: int,
    frame_h: int,
    is_death: bool = False,
) -> np.ndarray:
    """Scale a sprite to fit within target frame dimensions and place it.

    Scales uniformly to fill the frame as much as possible while
    maintaining aspect ratio, using LANCZOS interpolation. The sprite
    is centered horizontally and bottom-aligned (feet anchored) for
    upright poses. Death poses (lying down) are centered both ways.

    Args:
        sprite: Tightly cropped RGBA array.
        frame_w: Target frame width.
        frame_h: Target frame height.
        is_death: If True, center vertically instead of bottom-aligning.

    Returns:
        RGBA array of exactly (frame_h, frame_w, 4).
    """
    if sprite.size == 0:
        return np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    sh, sw = sprite.shape[:2]

    # Compute uniform scale to fit in frame (with 1px margin each side)
    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)
    scale = min(usable_w / sw, usable_h / sh)

    new_w = max(1, int(sw * scale))
    new_h = max(1, int(sh * scale))

    pil = Image.fromarray(sprite, "RGBA")
    pil_scaled = pil.resize((new_w, new_h), Image.LANCZOS)
    scaled_arr = np.array(pil_scaled)

    # Place in frame
    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)
    ph, pw = scaled_arr.shape[:2]

    # Clamp if somehow larger than frame
    if ph > frame_h:
        scaled_arr = scaled_arr[ph - frame_h:]
        ph = frame_h
    if pw > frame_w:
        offset = (pw - frame_w) // 2
        scaled_arr = scaled_arr[:, offset:offset + frame_w]
        pw = frame_w

    x_offset = (frame_w - pw) // 2

    if is_death:
        # Death pose: center vertically (lying down, not standing)
        y_offset = (frame_h - ph) // 2
    else:
        # Standard pose: bottom-align (feet anchored)
        y_offset = frame_h - ph

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = scaled_arr
    return frame


# ---------------------------------------------------------------------------
# Process a single source image
# ---------------------------------------------------------------------------

def process_single(
    source_path: Path,
    output_path: Path,
    frame_w: int,
    frame_h: int,
    expected_frames: int,
    is_death: bool = False,
) -> bool:
    """Process a single AI source image into a game-ready sprite sheet.

    Args:
        source_path: Path to the AI-generated source PNG.
        output_path: Path for the output sprite sheet PNG.
        frame_w: Width of each frame in the output.
        frame_h: Height of each frame in the output.
        expected_frames: Expected number of frames to extract.
        is_death: Whether this is a death animation (affects placement).

    Returns:
        True if processing succeeded, False otherwise.
    """
    if not source_path.exists():
        log.error("Source not found: %s", source_path)
        return False

    log.info("Processing: %s -> %s (%d frames, %dx%d each)",
             source_path.name, output_path.name, expected_frames,
             frame_w, frame_h)

    # Load source image
    img = np.array(Image.open(source_path))
    log.info("  Source size: %dx%d %s", img.shape[1], img.shape[0],
             "RGB" if img.shape[2] == 3 else "RGBA")

    # Step 1: Remove green background
    rgba = remove_green_background(img)

    # Step 2: Remove small components (labels, artifacts)
    cleaned = remove_small_components(rgba, min_area=5000)

    # Step 3: Detect sprite regions in cleaned image
    regions = detect_sprite_regions(cleaned, min_area=5000)

    if len(regions) == 0:
        log.error("  No sprite regions found in %s", source_path.name)
        return False

    if len(regions) != expected_frames:
        log.warning(
            "  Expected %d frames but found %d regions in %s",
            expected_frames, len(regions), source_path.name,
        )

    # Use the number of frames we actually found, up to expected count
    frame_count = min(len(regions), expected_frames)

    # Step 4: Crop each frame, clean green fringe, scale to target
    frames = []
    for i in range(frame_count):
        cropped = crop_region(cleaned, regions[i])
        cropped = clean_green_fringe(cropped)
        framed = scale_to_frame(cropped, frame_w, frame_h, is_death=is_death)
        frames.append(framed)
        log.info(
            "    Frame %d: cropped %dx%d -> placed in %dx%d",
            i + 1, cropped.shape[1], cropped.shape[0], frame_w, frame_h,
        )

    # If we found fewer frames than expected, duplicate the last frame
    while len(frames) < expected_frames:
        log.warning(
            "  Duplicating frame %d to fill expected count of %d",
            len(frames), expected_frames,
        )
        frames.append(frames[-1].copy())

    # Step 5: Assemble horizontal sprite sheet
    total_w = frame_w * len(frames)
    sheet = np.zeros((frame_h, total_w, 4), dtype=np.uint8)
    for i, frame in enumerate(frames):
        sheet[:, i * frame_w:(i + 1) * frame_w] = frame

    # Step 6: Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_img = Image.fromarray(sheet, "RGBA")
    out_img.save(str(output_path))

    log.info("  Saved: %s (%dx%d)", output_path.name, total_w, frame_h)
    return True


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def process_all(
    source_dir: Path,
    output_dir: Path,
    frame_w: int,
    frame_h: int,
    mapping: list[dict[str, Any]] | None = None,
) -> tuple[int, int]:
    """Process all source images according to the mapping.

    Args:
        source_dir: Directory containing AI source PNGs.
        output_dir: Directory for output sprite sheets.
        frame_w: Width of each frame.
        frame_h: Height of each frame.
        mapping: List of dicts with 'source', 'target', 'frames' keys.
            Defaults to RAMON_MAPPING.

    Returns:
        Tuple of (successes, failures).
    """
    if mapping is None:
        mapping = RAMON_MAPPING

    successes = 0
    failures = 0

    for entry in mapping:
        source_path = source_dir / entry["source"]
        target_path = output_dir / entry["target"]
        expected_frames = entry["frames"]
        is_death = entry["source"] == "death.png"

        ok = process_single(
            source_path=source_path,
            output_path=target_path,
            frame_w=frame_w,
            frame_h=frame_h,
            expected_frames=expected_frames,
            is_death=is_death,
        )

        if ok:
            successes += 1
        else:
            failures += 1

    return successes, failures


def main() -> None:
    """CLI entry point for processing Ramon AI sprites."""
    parser = argparse.ArgumentParser(
        description="Process AI-generated sprite sheets into game-ready format.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=PROJECT_ROOT / "assets" / "ai_sources" / "ramon",
        help="Directory containing AI source PNGs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "assets" / "sprites" / "ramon",
        help="Directory for output sprite sheets",
    )
    parser.add_argument(
        "--frame-width",
        type=int,
        default=48,
        help="Width of each frame in pixels (default: 48)",
    )
    parser.add_argument(
        "--frame-height",
        type=int,
        default=64,
        help="Height of each frame in pixels (default: 64)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("Ramon AI Sprite Processor")
    log.info("  Source: %s", args.source_dir)
    log.info("  Output: %s", args.output_dir)
    log.info("  Frame size: %dx%d", args.frame_width, args.frame_height)
    log.info("")

    successes, failures = process_all(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        frame_w=args.frame_width,
        frame_h=args.frame_height,
    )

    log.info("")
    log.info("Done: %d succeeded, %d failed", successes, failures)

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
