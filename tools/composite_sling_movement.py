"""Composite sling + movement sprites at full AI source resolution.

Takes AI source images (walk.png, jump.png, sling_attack.png) at their
original high resolution, extracts individual frames, and creates
composite sprites by combining:
  - Upper body from sling frames (arms/torso with sling)
  - Lower body from walk/jump frames (legs in motion)

This produces natural-looking sling-while-moving animations without
the seam artifacts of runtime compositing at 48x64 pixel resolution.

Output:
  assets/ai_sources/ramon/sling_walk.png  -- 6 frames
  assets/ai_sources/ramon/sling_jump.png  -- 2 frames

These are then processed by process_ramon_ai_sprites.py into final
game-ready sprite sheets at 48x64.

Usage:
    conda activate safona
    python tools/composite_sling_movement.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Reuse helpers from the processing pipeline.
from process_ramon_ai_sprites import (
    remove_green_background,
    remove_small_components,
    detect_sprite_regions,
    crop_region,
    clean_green_fringe,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_SOURCE_DIR = PROJECT_ROOT / "assets" / "ai_sources" / "ramon"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

GREEN_BG = (0, 255, 0)


# ---------------------------------------------------------------------------
# Frame extraction
# ---------------------------------------------------------------------------

def extract_frames(source_path: Path, expected: int) -> list[np.ndarray]:
    """Extract individual sprite frames from an AI source image.

    Removes the green background, filters small components (labels),
    detects sprite regions, crops each tightly, and cleans green fringe.

    Args:
        source_path: Path to the AI source PNG.
        expected: Expected number of frames.

    Returns:
        List of tightly-cropped RGBA numpy arrays.
    """
    if not source_path.exists():
        log.error("Source not found: %s", source_path)
        return []

    img = np.array(Image.open(source_path))
    log.info("Loaded %s: %dx%d", source_path.name, img.shape[1], img.shape[0])

    rgba = remove_green_background(img)
    cleaned = remove_small_components(rgba, min_area=5000)
    regions = detect_sprite_regions(cleaned, min_area=5000)

    if len(regions) < expected:
        log.warning(
            "Expected %d frames but found %d in %s",
            expected, len(regions), source_path.name,
        )

    frames = []
    for i, bbox in enumerate(regions[:expected]):
        cropped = crop_region(cleaned, bbox)
        cropped = clean_green_fringe(cropped)
        log.info(
            "  Frame %d: %dx%d",
            i + 1, cropped.shape[1], cropped.shape[0],
        )
        frames.append(cropped)

    return frames


# ---------------------------------------------------------------------------
# Normalize frames to uniform height (bottom-aligned)
# ---------------------------------------------------------------------------

def normalize_height(frames: list[np.ndarray]) -> list[np.ndarray]:
    """Normalize all frames to the same height, bottom-aligned.

    Pads shorter frames with transparent pixels at the top so all
    frames share the same height, aligning sprites by their feet.

    Args:
        frames: List of RGBA arrays of potentially different heights.

    Returns:
        List of RGBA arrays all with the same height.
    """
    if not frames:
        return frames

    max_h = max(f.shape[0] for f in frames)
    max_w = max(f.shape[1] for f in frames)

    result = []
    for f in frames:
        h, w = f.shape[:2]
        if h == max_h and w == max_w:
            result.append(f)
        else:
            padded = np.zeros((max_h, max_w, 4), dtype=np.uint8)
            # Bottom-align: place frame at bottom.
            y_off = max_h - h
            x_off = (max_w - w) // 2
            padded[y_off:y_off + h, x_off:x_off + w] = f
            result.append(padded)

    return result


# ---------------------------------------------------------------------------
# Composite upper + lower body
# ---------------------------------------------------------------------------

def composite_frame(
    upper_src: np.ndarray,
    lower_src: np.ndarray,
    split_ratio: float = 0.50,
    blend_rows: int = 3,
) -> np.ndarray:
    """Composite upper body from one frame with lower body from another.

    Both frames must be the same size (use normalize_height first).

    The split point is at ``split_ratio`` from the top of the sprite
    content (not the full frame). A small blend zone smooths the seam.

    Args:
        upper_src: RGBA array providing the upper body (sling pose).
        lower_src: RGBA array providing the lower body (walk/jump pose).
        split_ratio: Fraction from top where the split occurs (0.0-1.0).
        blend_rows: Number of pixel rows for alpha blending at the seam.

    Returns:
        Composited RGBA array.
    """
    assert upper_src.shape == lower_src.shape, (
        f"Frame shapes must match: {upper_src.shape} vs {lower_src.shape}"
    )

    h, w = upper_src.shape[:2]

    # Find content bounds (non-transparent rows) for each frame.
    upper_alpha = upper_src[:, :, 3]
    lower_alpha = lower_src[:, :, 3]

    upper_rows = np.any(upper_alpha > 0, axis=1)
    lower_rows = np.any(lower_alpha > 0, axis=1)

    if not np.any(upper_rows) or not np.any(lower_rows):
        return upper_src.copy()

    # Find the top of content in upper frame and bottom of content in lower.
    upper_top = int(np.where(upper_rows)[0][0])
    upper_bottom = int(np.where(upper_rows)[0][-1])
    lower_top = int(np.where(lower_rows)[0][0])
    lower_bottom = int(np.where(lower_rows)[0][-1])

    # The split line is relative to the combined content span.
    # Use the union of both frames' content to find the split.
    content_top = min(upper_top, lower_top)
    content_bottom = max(upper_bottom, lower_bottom)
    content_h = content_bottom - content_top + 1

    split_y = content_top + int(content_h * split_ratio)

    # Build the composite.
    result = np.zeros_like(upper_src)

    # Top half: from upper_src.
    result[:split_y] = upper_src[:split_y]

    # Bottom half: from lower_src.
    result[split_y:] = lower_src[split_y:]

    # Blend zone around the split.
    blend_start = max(0, split_y - blend_rows)
    blend_end = min(h, split_y + blend_rows)

    for y in range(blend_start, blend_end):
        # t = 0 at blend_start (fully upper), 1 at blend_end (fully lower).
        t = (y - blend_start) / max(1, blend_end - blend_start - 1)

        upper_pixel = upper_src[y].astype(np.float32)
        lower_pixel = lower_src[y].astype(np.float32)

        # Only blend where both have content.
        upper_has = upper_src[y, :, 3] > 0
        lower_has = lower_src[y, :, 3] > 0
        both = upper_has & lower_has

        # Where both exist, blend.
        blended = (1.0 - t) * upper_pixel + t * lower_pixel
        result[y][both] = blended[both].astype(np.uint8)

        # Where only upper exists and we're in top half, keep upper.
        upper_only = upper_has & ~lower_has
        if t < 0.5:
            result[y][upper_only] = upper_src[y][upper_only]

        # Where only lower exists and we're in bottom half, keep lower.
        lower_only = ~upper_has & lower_has
        if t >= 0.5:
            result[y][lower_only] = lower_src[y][lower_only]

    return result


# ---------------------------------------------------------------------------
# Assemble frames onto green background with numbered labels
# ---------------------------------------------------------------------------

def assemble_on_green(
    frames: list[np.ndarray],
    padding: int = 40,
    top_margin: int = 60,
    bottom_margin: int = 40,
) -> Image.Image:
    """Place composited frames onto a green background with number labels.

    Mimics the layout of the original AI source images so the processing
    pipeline can handle them identically.

    Args:
        frames: List of RGBA numpy arrays (all same size).
        padding: Horizontal padding between frames.
        top_margin: Space above sprites for number labels.
        bottom_margin: Space below sprites.

    Returns:
        PIL Image with green background and numbered frames.
    """
    if not frames:
        return Image.new("RGB", (100, 100), GREEN_BG)

    frame_h, frame_w = frames[0].shape[:2]
    n = len(frames)

    total_w = padding + n * (frame_w + padding)
    total_h = top_margin + frame_h + bottom_margin

    canvas = Image.new("RGBA", (total_w, total_h), (*GREEN_BG, 255))

    for i, frame_arr in enumerate(frames):
        x = padding + i * (frame_w + padding)
        y = top_margin

        frame_img = Image.fromarray(frame_arr, "RGBA")
        canvas.paste(frame_img, (x, y), frame_img)

    # Add number labels above each frame.
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i in range(n):
        x = padding + i * (frame_w + padding) + frame_w // 2
        y_label = top_margin - 35
        draw.text(
            (x, y_label),
            str(i + 1),
            fill=(255, 255, 255, 255),
            font=font,
            anchor="mt",
        )

    # Convert to RGB (green background, no transparency needed for source).
    result = Image.new("RGB", (total_w, total_h), GREEN_BG)
    result.paste(canvas, (0, 0), canvas)

    return result


# ---------------------------------------------------------------------------
# Main compositing pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate composite sling+movement AI source sprites."""
    log.info("=== Sling Movement Compositor ===")
    log.info("Source dir: %s", AI_SOURCE_DIR)

    # Extract frames from each source.
    walk_frames = extract_frames(AI_SOURCE_DIR / "walk.png", expected=6)
    jump_frames = extract_frames(AI_SOURCE_DIR / "jump.png", expected=2)
    sling_frames = extract_frames(AI_SOURCE_DIR / "sling_attack.png", expected=3)

    if not walk_frames or not jump_frames or not sling_frames:
        log.error("Failed to extract frames from one or more sources.")
        sys.exit(1)

    log.info("")
    log.info("Extracted: %d walk, %d jump, %d sling frames",
             len(walk_frames), len(jump_frames), len(sling_frames))

    # Normalize all frames to the same height (bottom-aligned).
    all_frames = walk_frames + jump_frames + sling_frames
    normalized = normalize_height(all_frames)

    n_walk = len(walk_frames)
    n_jump = len(jump_frames)
    n_sling = len(sling_frames)

    norm_walk = normalized[:n_walk]
    norm_jump = normalized[n_walk:n_walk + n_jump]
    norm_sling = normalized[n_walk + n_jump:]

    log.info("Normalized to uniform size: %dx%d",
             normalized[0].shape[1], normalized[0].shape[0])

    # --- Composite sling_walk: 6 frames ---
    # Upper body: alternate sling charge frame 0 and 1.
    # Lower body: cycle through 6 walk positions.
    log.info("")
    log.info("Compositing sling_walk (6 frames)...")
    sling_walk_composites = []
    for i in range(6):
        sling_idx = i % 2  # Alternate between frame 0 and 1.
        upper = norm_sling[sling_idx]
        lower = norm_walk[i]
        comp = composite_frame(upper, lower, split_ratio=0.50, blend_rows=3)
        sling_walk_composites.append(comp)
        log.info("  Frame %d: sling[%d] upper + walk[%d] lower",
                 i + 1, sling_idx + 1, i + 1)

    # --- Composite sling_jump: 2 frames ---
    # Frame 0: sling charge 0 + jump 0.
    # Frame 1: sling charge 1 + jump 1.
    log.info("")
    log.info("Compositing sling_jump (2 frames)...")
    sling_jump_composites = []
    for i in range(2):
        upper = norm_sling[i]
        lower = norm_jump[i]
        comp = composite_frame(upper, lower, split_ratio=0.50, blend_rows=3)
        sling_jump_composites.append(comp)
        log.info("  Frame %d: sling[%d] upper + jump[%d] lower",
                 i + 1, i + 1, i + 1)

    # Assemble onto green backgrounds with labels.
    log.info("")
    log.info("Assembling onto green backgrounds...")

    sling_walk_img = assemble_on_green(sling_walk_composites)
    sling_jump_img = assemble_on_green(sling_jump_composites)

    # Save.
    out_walk = AI_SOURCE_DIR / "sling_walk.png"
    out_jump = AI_SOURCE_DIR / "sling_jump.png"

    sling_walk_img.save(str(out_walk))
    sling_jump_img.save(str(out_jump))

    log.info("Saved: %s (%dx%d)", out_walk.name,
             sling_walk_img.width, sling_walk_img.height)
    log.info("Saved: %s (%dx%d)", out_jump.name,
             sling_jump_img.width, sling_jump_img.height)

    log.info("")
    log.info("Done! Now run process_ramon_ai_sprites.py to generate game sprites.")


if __name__ == "__main__":
    main()
