"""Generic sprite processor for AI-generated source images.

Takes AI source images on green (#00FF00) backgrounds and produces
game-ready sprite sheets. Works from a JSON configuration that
specifies input paths, pose indices, output paths, and target
frame dimensions.

The pipeline:
1. Remove green chroma-key background
2. Detect pose regions via scipy.ndimage.label (filter < 500px area)
3. Crop each pose with inset to remove green fringe
4. Replace remaining green pixels with neighbor-averaged colors
5. Scale: LANCZOS to intermediate -> NEAREST to final size
6. Center horizontally, bottom-align (feet anchored) in target frame
7. Hard-threshold alpha (< 100 = transparent, >= 100 = opaque)
8. Check facing direction (sprites should face RIGHT by default)
9. Assemble poses into horizontal sprite sheets

Usage:
    conda activate safona
    python tools/process_ai_sprites.py [config.json]
    python tools/process_ai_sprites.py --config-inline '{"sources": [...]}'

Config format:
    {
      "sources": [
        {
          "input": "assets/ai_sources/bep/image.png",
          "outputs": [
            {
              "file": "assets/sprites/bep/idle.png",
              "poses": [1, 2, 3, 4],
              "frame_width": 16,
              "frame_height": 16
            }
          ]
        }
      ]
    }

Pose indices are 1-based (pose 1 = first detected region).
"""

from __future__ import annotations

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
# Pose detection via connected components
# ---------------------------------------------------------------------------

def detect_poses(
    rgba: np.ndarray,
    min_area: int = 500,
) -> list[tuple[int, int, int, int]]:
    """Detect individual pose regions using connected-component labeling.

    Args:
        rgba: RGBA image array with green removed.
        min_area: Minimum pixel area for a region to be kept.

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
            continue
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        regions.append((x0, y0, x1, y1, area))

    # Sort left-to-right by x0
    regions.sort(key=lambda r: r[0])
    return [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in regions]


# ---------------------------------------------------------------------------
# Crop and clean a single pose
# ---------------------------------------------------------------------------

def crop_and_clean_pose(
    rgba: np.ndarray,
    bbox: tuple[int, int, int, int],
    inset: int = 4,
) -> np.ndarray:
    """Crop a single pose from the full image, cleaning green fringe.

    Applies an inset to avoid green border artifacts, then replaces
    any remaining green-ish pixels with their neighbor average.

    Args:
        rgba: Full RGBA image array.
        bbox: (x0, y0, x1, y1) bounding box.
        inset: Pixels to trim from each edge inside the bbox.

    Returns:
        Tightly cropped and cleaned RGBA array of the pose.
    """
    x0, y0, x1, y1 = bbox

    # Apply inset
    ix0 = min(x0 + inset, x1)
    iy0 = min(y0 + inset, y1)
    ix1 = max(x1 - inset, ix0)
    iy1 = max(y1 - inset, iy0)

    crop = rgba[iy0:iy1, ix0:ix1].copy()

    if crop.size == 0:
        return crop

    # Clean remaining green pixels via neighbor averaging
    _clean_green_fringe(crop)

    # Tight crop around actual content
    alpha = crop[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)

    if not np.any(rows):
        return crop

    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    return crop[r0:r1 + 1, c0:c1 + 1]


def _clean_green_fringe(crop: np.ndarray) -> None:
    """Replace remaining green-ish pixels with neighbor average (in-place).

    Uses a slightly relaxed green test to catch fringe pixels that
    survived the initial chroma removal.

    Args:
        crop: RGBA numpy array (modified in place).
    """
    r = crop[:, :, 0].astype(np.int32)
    g = crop[:, :, 1].astype(np.int32)
    b = crop[:, :, 2].astype(np.int32)
    a = crop[:, :, 3]

    # Relaxed green detection for fringe
    green_mask = (g - r > 30) & (g - b > 30) & (g > 100) & (a > 0)

    if not np.any(green_mask):
        return

    h, w = crop.shape[:2]
    gy, gx = np.where(green_mask)

    for cy, cx in zip(gy, gx):
        neighbors = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if not green_mask[ny, nx] and crop[ny, nx, 3] > 0:
                        neighbors.append(crop[ny, nx, :3].astype(np.float32))
        if neighbors:
            avg = np.mean(neighbors, axis=0).astype(np.uint8)
            crop[cy, cx, :3] = avg
        else:
            # No valid neighbors: make transparent
            crop[cy, cx, 3] = 0


# ---------------------------------------------------------------------------
# Scaling pipeline: LANCZOS intermediate -> NEAREST final
# ---------------------------------------------------------------------------

def scale_pose_to_frame(
    pose: np.ndarray,
    frame_w: int,
    frame_h: int,
) -> np.ndarray:
    """Scale a pose to fit within target frame dimensions.

    Uses a two-step approach: LANCZOS to an intermediate size
    (2x target) then NEAREST to final, preserving pixel-art quality.

    The pose is scaled uniformly to fill the frame as much as possible
    while maintaining aspect ratio.

    Args:
        pose: Tightly cropped RGBA array.
        frame_w: Target frame width.
        frame_h: Target frame height.

    Returns:
        Scaled RGBA array that fits within frame_w x frame_h.
    """
    if pose.size == 0:
        return np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    ph, pw = pose.shape[:2]

    # Compute uniform scale to fit in frame (with 1px margin)
    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)
    scale = min(usable_w / pw, usable_h / ph)

    # Intermediate size at 2x for LANCZOS quality
    inter_w = max(1, int(pw * scale * 2))
    inter_h = max(1, int(ph * scale * 2))

    # Final size
    final_w = max(1, int(pw * scale))
    final_h = max(1, int(ph * scale))

    pil = Image.fromarray(pose, "RGBA")

    # Step 1: LANCZOS to intermediate
    pil_inter = pil.resize((inter_w, inter_h), Image.LANCZOS)
    # Step 2: NEAREST to final
    pil_final = pil_inter.resize((final_w, final_h), Image.NEAREST)

    return np.array(pil_final)


# ---------------------------------------------------------------------------
# Frame placement
# ---------------------------------------------------------------------------

def place_in_frame(
    pose: np.ndarray,
    frame_w: int,
    frame_h: int,
) -> np.ndarray:
    """Place a scaled pose into a fixed-size frame.

    Centers horizontally and bottom-aligns (feet anchored).

    Args:
        pose: Scaled RGBA pose array.
        frame_w: Target frame width.
        frame_h: Target frame height.

    Returns:
        RGBA array of size (frame_h, frame_w, 4).
    """
    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    if pose.size == 0:
        return frame

    ph, pw = pose.shape[:2]

    # Clamp if pose exceeds frame
    if ph > frame_h:
        pose = pose[ph - frame_h:]
        ph = frame_h
    if pw > frame_w:
        offset = (pw - frame_w) // 2
        pose = pose[:, offset:offset + frame_w]
        pw = frame_w

    y_offset = frame_h - ph
    x_offset = (frame_w - pw) // 2

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = pose
    return frame


# ---------------------------------------------------------------------------
# Alpha thresholding
# ---------------------------------------------------------------------------

def hard_threshold_alpha(rgba: np.ndarray, threshold: int = 100) -> np.ndarray:
    """Apply hard alpha threshold: below = 0, above = 255.

    Args:
        rgba: RGBA numpy array.
        threshold: Alpha cutoff value.

    Returns:
        Modified RGBA array with binary alpha.
    """
    result = rgba.copy()
    result[:, :, 3] = np.where(result[:, :, 3] < threshold, 0, 255)
    return result


# ---------------------------------------------------------------------------
# Facing direction check
# ---------------------------------------------------------------------------

def check_facing_right(pose: np.ndarray) -> bool:
    """Check if a pose appears to face right.

    Compares center of mass of the left half vs right half.
    If more pixel mass is on the left side (features pointing right),
    the sprite faces right.

    Args:
        pose: RGBA numpy array.

    Returns:
        True if sprite appears to face right (or is symmetric).
    """
    alpha = pose[:, :, 3]
    h, w = alpha.shape
    if w < 2 or not np.any(alpha > 0):
        return True

    mid = w // 2
    left_mass = np.sum(alpha[:, :mid].astype(np.float64))
    right_mass = np.sum(alpha[:, mid:].astype(np.float64))

    # If right half has significantly more mass, sprite likely faces left
    # (the "front" of the character has more detail/width)
    # A 20% threshold avoids false positives on symmetric sprites
    if right_mass > left_mass * 1.2:
        return False
    return True


def ensure_facing_right(pose: np.ndarray, label: str = "") -> np.ndarray:
    """Flip pose horizontally if it appears to face left.

    Args:
        pose: RGBA numpy array.
        label: Label for logging.

    Returns:
        Original or flipped pose.
    """
    if not check_facing_right(pose):
        log.info("Flipped sprite to face right: %s", label)
        return pose[:, ::-1].copy()
    return pose


# ---------------------------------------------------------------------------
# Sprite sheet assembly
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


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

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
# Placeholder generation (when AI source not available)
# ---------------------------------------------------------------------------

def generate_placeholder_sheet(
    frame_w: int,
    frame_h: int,
    frame_count: int,
    color: tuple[int, int, int, int] = (180, 80, 180, 255),
    output_path: Path | None = None,
) -> np.ndarray:
    """Generate a simple colored-rectangle placeholder sprite sheet.

    Each frame is a filled rectangle with a 1px darker border,
    providing visual distinction in-game.

    Args:
        frame_w: Frame width in pixels.
        frame_h: Frame height in pixels.
        frame_count: Number of frames.
        color: RGBA fill color.
        output_path: If provided, save to this path.

    Returns:
        RGBA numpy array of the placeholder sheet.
    """
    sheet = np.zeros((frame_h, frame_w * frame_count, 4), dtype=np.uint8)

    # Darker border color
    border = (
        max(0, color[0] - 60),
        max(0, color[1] - 60),
        max(0, color[2] - 60),
        color[3],
    )

    for i in range(frame_count):
        x0 = i * frame_w
        # Fill
        sheet[1:frame_h - 1, x0 + 1:x0 + frame_w - 1] = color
        # Border
        sheet[0, x0:x0 + frame_w] = border
        sheet[frame_h - 1, x0:x0 + frame_w] = border
        sheet[:, x0] = border
        sheet[:, x0 + frame_w - 1] = border

    if output_path:
        save_sheet(sheet, output_path)

    return sheet


# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------

def process_source(source_config: dict[str, Any]) -> dict[str, Any]:
    """Process a single AI source image into sprite sheets.

    Args:
        source_config: Dict with 'input' path and 'outputs' list.

    Returns:
        Dict with results: {'processed': [...], 'errors': [...]}
    """
    input_rel = source_config["input"]
    input_path = PROJECT_ROOT / input_rel
    outputs = source_config["outputs"]

    results: dict[str, Any] = {"processed": [], "errors": []}

    if not input_path.exists():
        log.warning("AI source not found: %s -- generating placeholders", input_path)
        for out_cfg in outputs:
            out_path = PROJECT_ROOT / out_cfg["file"]
            fw = out_cfg["frame_width"]
            fh = out_cfg["frame_height"]
            poses = out_cfg.get("poses", [1])
            fc = len(poses)

            # Pick color based on output category
            color = _color_for_path(out_cfg["file"])
            generate_placeholder_sheet(fw, fh, fc, color, out_path)
            results["processed"].append(out_cfg["file"])
        return results

    # Load and remove green background
    log.info("Processing: %s", input_rel)
    img = np.array(Image.open(input_path))
    log.info("  Image size: %dx%d", img.shape[1], img.shape[0])

    rgba = remove_green_background(img)
    log.info("  Green removal complete")

    # Detect poses (min_area filters out small label regions in AI images)
    min_area = source_config.get("min_area", 500)
    pose_bboxes = detect_poses(rgba, min_area=min_area)
    log.info("  Detected %d poses (>= 500px area)", len(pose_bboxes))

    for i, (x0, y0, x1, y1) in enumerate(pose_bboxes):
        log.info("    Pose %d: bbox=(%d,%d)-(%d,%d) w=%d h=%d",
                 i + 1, x0, y0, x1, y1, x1 - x0, y1 - y0)

    # Crop and clean all poses
    poses = [crop_and_clean_pose(rgba, bb) for bb in pose_bboxes]
    log.info("  Cropped %d poses", len(poses))

    # Process each output entry
    for out_cfg in outputs:
        out_path = PROJECT_ROOT / out_cfg["file"]
        fw = out_cfg["frame_width"]
        fh = out_cfg["frame_height"]
        pose_indices = out_cfg.get("poses", [1])

        # Validate pose indices
        max_pose = len(poses)
        valid_indices = [i for i in pose_indices if 1 <= i <= max_pose]

        if len(valid_indices) < len(pose_indices):
            missing = [i for i in pose_indices if i not in valid_indices]
            log.warning("  %s: poses %s not found (max=%d), using available",
                        out_cfg["file"], missing, max_pose)

        if not valid_indices:
            log.warning("  %s: no valid poses, generating placeholder", out_cfg["file"])
            color = _color_for_path(out_cfg["file"])
            generate_placeholder_sheet(fw, fh, len(pose_indices), color, out_path)
            results["processed"].append(out_cfg["file"])
            continue

        # Scale, frame, threshold, check facing for each pose
        frames = []
        for idx in valid_indices:
            pose = poses[idx - 1]  # 1-based to 0-based
            scaled = scale_pose_to_frame(pose, fw, fh)
            framed = place_in_frame(scaled, fw, fh)
            framed = hard_threshold_alpha(framed)
            framed = ensure_facing_right(
                framed,
                label=f"{out_cfg['file']} pose {idx}",
            )
            frames.append(framed)

        # Assemble and save
        sheet = assemble_sheet(frames)
        save_sheet(sheet, out_path)
        results["processed"].append(out_cfg["file"])

    return results


def _color_for_path(file_path: str) -> tuple[int, int, int, int]:
    """Choose a placeholder color based on the output path category.

    Args:
        file_path: Relative output path.

    Returns:
        RGBA color tuple.
    """
    p = file_path.lower()
    if "boss" in p:
        return (200, 60, 60, 255)  # Red for boss
    if "enemy" in p or "rival" in p or "guardian" in p or "sheep" in p:
        return (200, 100, 50, 255)  # Orange for enemies
    if "pickup" in p or "heart" in p or "shield" in p:
        return (100, 200, 100, 255)  # Green for pickups
    if "breakable" in p or "pot" in p or "crate" in p:
        return (160, 140, 100, 255)  # Brown for breakables
    if "projectile" in p or "stone_tier" in p:
        return (150, 150, 170, 255)  # Grey for projectiles
    if "portrait" in p:
        return (180, 160, 140, 255)  # Tan for portraits
    if "effect" in p or "fx" in p or "dust" in p or "impact" in p or "aura" in p or "portal" in p:
        return (140, 140, 220, 255)  # Blue for effects
    if "npc" in p or "dimoni" in p or "llorencc" in p:
        return (160, 100, 180, 255)  # Purple for NPCs
    if "bep" in p:
        return (180, 160, 120, 255)  # Warm brown for Bep
    return (180, 80, 180, 255)  # Default magenta


# ---------------------------------------------------------------------------
# Config loading and CLI
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path | None = None, inline: str | None = None) -> dict[str, Any]:
    """Load processing configuration from file or inline JSON.

    Args:
        config_path: Path to JSON config file.
        inline: Inline JSON string.

    Returns:
        Parsed configuration dict.
    """
    if inline:
        return json.loads(inline)
    if config_path:
        with open(config_path) as f:
            return json.load(f)
    raise ValueError("Either config_path or inline JSON required")


def main() -> None:
    """Process all AI source images according to config."""
    # Parse CLI args
    config_path = None
    inline = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--config-inline":
            inline = args[i + 1]
            i += 2
        else:
            config_path = args[i]
            i += 1

    if not config_path and not inline:
        # Default: look for process_all_sprites_config.json
        default_config = PROJECT_ROOT / "tools" / "process_all_sprites_config.json"
        if default_config.exists():
            config_path = str(default_config)
        else:
            log.error("No config specified. Usage: process_ai_sprites.py <config.json>")
            log.error("  or: process_ai_sprites.py --config-inline '{\"sources\": [...]}'")
            sys.exit(1)

    config = load_config(config_path, inline)
    sources = config.get("sources", [])

    log.info("Processing %d source entries...", len(sources))

    total_processed = 0
    total_errors = 0

    for source_cfg in sources:
        result = process_source(source_cfg)
        total_processed += len(result["processed"])
        total_errors += len(result["errors"])

    log.info("")
    log.info("Done: %d sheets processed, %d errors", total_processed, total_errors)

    if total_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
