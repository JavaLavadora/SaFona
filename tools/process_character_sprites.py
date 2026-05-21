#!/usr/bin/env python3
"""Process AI-generated character sprite sources into game-ready sprite sheets.

A standalone CLI tool that reads a simple JSON config per character and
produces properly scaled, snapped, horizontal sprite sheets.

Usage:
    python tools/process_character_sprites.py tools/sprite_defs/characters/ramon.json
    python tools/process_character_sprites.py tools/sprite_defs/characters/*.json
    python tools/process_character_sprites.py -v tools/sprite_defs/characters/ramon.json

Config format (JSON):
    {
      "frame_width": 48,
      "frame_height": 64,
      "source_dir": "assets/ai_sources/ramon",
      "output_dir": "assets/sprites/ramon",
      "animations": [
        {"source": "idle.png", "frames": 4, "scale_pct": 80},
        {"source": "sling_attack.png", "output": "sling.png", "frames": 3, "scale_pct": 100},
        {"source": "jump.png", "frames": 2, "scale_pct": 85, "vertical_snap": "center"},
        {"source": "death.png", "frames": 1, "scale_pct": 100}
      ]
    }

scale_pct:
    Percentage of frame_height the tallest frame should occupy.
    100 = fills the full frame height. 80 = fills 80% of frame height.
    You decide this per animation by inspecting the art.

vertical_snap / horizontal_snap:
    Where to place the sprite in the frame. Defaults: bottom / center.
    Allowed: "top", "bottom", "center" / "left", "right", "center".
    If the scaled sprite overflows, it is clipped from the opposite side.
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
    """Remove green chroma-key background and return RGBA array."""
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
    """Remove connected components below min_area pixels."""
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

    Returns list of (x0, y0, x1, y1) bounding boxes, sorted left-to-right.
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
    """Crop a region and tight-crop to non-transparent content."""
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
    """Replace green-tinted edge pixels with neighbor color averages."""
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
    """Scale a sprite using LANCZOS interpolation."""
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
    vertical_snap: str = "bottom",
    horizontal_snap: str = "center",
) -> np.ndarray:
    """Place a scaled sprite into a fixed-size frame.

    If the scaled sprite overflows, it is clipped from the opposite side
    of the snap direction.
    """
    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    if scaled.size == 0:
        return frame

    ph, pw = scaled.shape[:2]

    # --- Vertical clipping ---
    if ph > frame_h:
        if vertical_snap == "bottom":
            scaled = scaled[ph - frame_h:]
        elif vertical_snap == "top":
            scaled = scaled[:frame_h]
        else:
            top_clip = (ph - frame_h) // 2
            scaled = scaled[top_clip:top_clip + frame_h]
        ph = frame_h

    # --- Horizontal clipping ---
    if pw > frame_w:
        if horizontal_snap == "right":
            scaled = scaled[:, pw - frame_w:]
        elif horizontal_snap == "left":
            scaled = scaled[:, :frame_w]
        else:
            left_clip = (pw - frame_w) // 2
            scaled = scaled[:, left_clip:left_clip + frame_w]
        pw = frame_w

    # --- Vertical placement ---
    if vertical_snap == "bottom":
        y_offset = frame_h - ph
    elif vertical_snap == "top":
        y_offset = 0
    else:
        y_offset = (frame_h - ph) // 2

    # --- Horizontal placement ---
    if horizontal_snap == "right":
        x_offset = frame_w - pw
    elif horizontal_snap == "left":
        x_offset = 0
    else:
        x_offset = (frame_w - pw) // 2

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = scaled
    return frame


# ---------------------------------------------------------------------------
# Sprite sheet assembly and saving
# ---------------------------------------------------------------------------

def assemble_sheet(frames: list[np.ndarray]) -> np.ndarray:
    """Assemble frames into a horizontal sprite sheet."""
    if not frames:
        return np.zeros((1, 1, 4), dtype=np.uint8)

    h, w = frames[0].shape[:2]
    sheet = np.zeros((h, w * len(frames), 4), dtype=np.uint8)
    for i, frame in enumerate(frames):
        sheet[:, i * w:(i + 1) * w] = frame
    return sheet


def save_sheet(sheet: np.ndarray, path: Path) -> None:
    """Save an RGBA sheet as PNG."""
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

    For each animation:
    1. Load source, remove green background, remove small components,
       detect sprite regions, crop each frame, clean green fringe.
    2. Compute scale from scale_pct: target_h = frame_h * scale_pct / 100,
       scale = target_h / max_crop_h. All frames share the same scale.
    3. Scale each frame, place in frame using snap settings, assemble
       into horizontal sprite sheet, save as PNG.
    """
    with open(config_path) as f:
        config = json.load(f)

    frame_w: int = config["frame_width"]
    frame_h: int = config["frame_height"]
    source_dir = PROJECT_ROOT / config["source_dir"]
    output_dir = PROJECT_ROOT / config["output_dir"]
    anim_entries: list[dict[str, Any]] = config["animations"]

    log.info("Character: %s", config_path.stem)
    log.info("  Frame: %dx%d, %d animations", frame_w, frame_h, len(anim_entries))

    successes = 0
    failures = 0

    for entry in anim_entries:
        source_path = source_dir / entry["source"]
        output_name = entry.get("output", entry["source"])
        output_path = output_dir / output_name
        expected_frames: int = entry["frames"]
        scale_pct: float = entry["scale_pct"]
        v_snap: str = entry.get("vertical_snap", "bottom")
        h_snap: str = entry.get("horizontal_snap", "center")

        if not source_path.exists():
            log.error("  Source not found: %s", source_path)
            failures += 1
            continue

        log.info(
            "  %s: %d frames, scale=%d%%, snap=%s/%s",
            source_path.name, expected_frames, scale_pct, v_snap, h_snap,
        )

        # --- Load, clean, detect, crop ---
        img = np.array(Image.open(source_path))
        rgba = remove_green_background(img)
        cleaned = remove_small_components(rgba, min_area=5000)
        bboxes = detect_sprite_regions(cleaned, min_area=5000)

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

        while len(cropped_frames) < expected_frames:
            cropped_frames.append(cropped_frames[-1].copy())

        # --- Compute scale from scale_pct ---
        max_crop_h = max(c.shape[0] for c in cropped_frames)
        target_h = frame_h * (scale_pct / 100.0)
        scale = target_h / max_crop_h

        log.debug(
            "    max_crop_h=%d, target_h=%.1f, scale=%.4f",
            max_crop_h, target_h, scale,
        )

        # --- Scale, place, assemble ---
        placed_frames: list[np.ndarray] = []
        for i, cropped in enumerate(cropped_frames):
            scaled = scale_sprite(cropped, scale)
            placed = place_in_frame(scaled, frame_w, frame_h, v_snap, h_snap)
            placed_frames.append(placed)
            log.debug(
                "    Frame %d: %dx%d -> %dx%d (scale=%.4f)",
                i + 1, cropped.shape[1], cropped.shape[0],
                scaled.shape[1], scaled.shape[0], scale,
            )

        sheet = assemble_sheet(placed_frames)
        save_sheet(sheet, output_path)
        successes += 1

    return successes, failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Process AI-generated sprite sources into game-ready sprite sheets.",
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
    """Entry point."""
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
