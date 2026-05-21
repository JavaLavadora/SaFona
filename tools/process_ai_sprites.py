"""Generic sprite processor for AI-generated source images.

Takes AI source images on green backgrounds and produces
game-ready sprite sheets. Supports two modes of operation:

**Directory mode** (recommended for batch processing a character):
    python tools/process_ai_sprites.py <source_dir> <output_dir> \\
        --frame-width 48 --frame-height 64 \\
        --mapping idle:4 walk:6 jump:2 wall_slide:2 wall_jump:2 \\
                 "sling_attack>sling:3" hit:1 death:1

    Mapping format: ``source_name:frame_count`` or
    ``source_name>output_name:frame_count`` for renaming.

**Config mode** (legacy, for complex multi-source pipelines):
    python tools/process_ai_sprites.py [config.json]
    python tools/process_ai_sprites.py --config-inline '{"sources": [...]}'

The pipeline:
1. Remove green chroma-key background (heuristic: G > 80, G-R > 40, G-B > 40)
2. Remove small connected components (< 5000px area: number labels, artifacts)
3. Detect sprite regions via scipy.ndimage.label
4. Crop each frame to bounding box content
5. Clean green fringe pixels via neighbor averaging
6. Scale to target frame size using NEAREST interpolation (pixel art)
7. Center horizontally, bottom-align (feet anchored); death poses centered vertically
8. Assemble frames into a horizontal sprite sheet
9. Save as RGBA PNG
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
# Scaling pipeline: LANCZOS
# ---------------------------------------------------------------------------

def scale_pose_to_frame(
    pose: np.ndarray,
    frame_w: int,
    frame_h: int,
) -> np.ndarray:
    """Scale a pose to fit within target frame dimensions.

    Uses LANCZOS interpolation for smooth downscaling that preserves
    gradients and produces anti-aliased edges.

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

    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)
    scale = min(usable_w / pw, usable_h / ph)

    final_w = max(1, int(pw * scale))
    final_h = max(1, int(ph * scale))

    pil = Image.fromarray(pose, "RGBA")
    pil_final = pil.resize((final_w, final_h), Image.LANCZOS)

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


# ---------------------------------------------------------------------------
# Directory-mode processing (--mapping CLI)
# ---------------------------------------------------------------------------

def _remove_small_components(
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


def _crop_region(rgba: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
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


def _clean_green_fringe(crop: np.ndarray) -> np.ndarray:
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


def _scale_to_frame(
    sprite: np.ndarray,
    frame_w: int,
    frame_h: int,
    is_death: bool = False,
) -> np.ndarray:
    """Scale a sprite into target frame using LANCZOS interpolation.

    Centers horizontally, bottom-aligns (feet anchored) for normal
    poses. Death poses are centered vertically.

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

    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)
    scale = min(usable_w / sw, usable_h / sh)

    new_w = max(1, int(sw * scale))
    new_h = max(1, int(sh * scale))

    pil = Image.fromarray(sprite, "RGBA")
    pil_scaled = pil.resize((new_w, new_h), Image.LANCZOS)
    scaled_arr = np.array(pil_scaled)

    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)
    ph, pw = scaled_arr.shape[:2]

    if ph > frame_h:
        scaled_arr = scaled_arr[ph - frame_h:]
        ph = frame_h
    if pw > frame_w:
        offset = (pw - frame_w) // 2
        scaled_arr = scaled_arr[:, offset:offset + frame_w]
        pw = frame_w

    x_offset = (frame_w - pw) // 2

    y_offset = frame_h - ph

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = scaled_arr
    return frame


def _scale_to_frame_uniform(
    sprite: np.ndarray,
    frame_w: int,
    frame_h: int,
    scale: float,
    is_death: bool = False,
) -> np.ndarray:
    """Scale a sprite using a pre-computed uniform scale factor.

    All frames in an animation share the same scale so characters
    stay the same size across poses.

    Args:
        sprite: Tightly cropped RGBA array.
        frame_w: Target frame width.
        frame_h: Target frame height.
        scale: Uniform scale factor (computed from the largest frame).
        is_death: If True, center vertically instead of bottom-aligning.

    Returns:
        RGBA array of exactly (frame_h, frame_w, 4).
    """
    if sprite.size == 0:
        return np.zeros((frame_h, frame_w, 4), dtype=np.uint8)

    sh, sw = sprite.shape[:2]
    new_w = max(1, int(sw * scale))
    new_h = max(1, int(sh * scale))

    pil = Image.fromarray(sprite, "RGBA")
    pil_scaled = pil.resize((new_w, new_h), Image.LANCZOS)
    scaled_arr = np.array(pil_scaled)

    frame = np.zeros((frame_h, frame_w, 4), dtype=np.uint8)
    ph, pw = scaled_arr.shape[:2]

    if ph > frame_h:
        scaled_arr = scaled_arr[ph - frame_h:]
        ph = frame_h
    if pw > frame_w:
        offset = (pw - frame_w) // 2
        scaled_arr = scaled_arr[:, offset:offset + frame_w]
        pw = frame_w

    x_offset = (frame_w - pw) // 2

    y_offset = frame_h - ph

    frame[y_offset:y_offset + ph, x_offset:x_offset + pw] = scaled_arr
    return frame


def parse_mapping(mapping_strs: list[str]) -> list[dict[str, Any]]:
    """Parse CLI mapping arguments into structured entries.

    Each mapping string is ``source_name:frame_count`` or
    ``source_name>output_name:frame_count``.

    Args:
        mapping_strs: List of mapping strings from the CLI.

    Returns:
        List of dicts with 'source', 'target', 'frames' keys.
    """
    entries = []
    for s in mapping_strs:
        # Split on last colon to get frame count
        if ":" not in s:
            log.error("Invalid mapping format: %s (expected name:count)", s)
            continue

        name_part, count_str = s.rsplit(":", 1)
        try:
            frame_count = int(count_str)
        except ValueError:
            log.error("Invalid frame count in mapping: %s", s)
            continue

        # Check for rename: source_name>output_name
        if ">" in name_part:
            source_name, output_name = name_part.split(">", 1)
        else:
            source_name = name_part
            output_name = name_part

        entries.append({
            "source": f"{source_name}.png",
            "target": f"{output_name}.png",
            "frames": frame_count,
        })

    return entries


def process_directory(
    source_dir: Path,
    output_dir: Path,
    frame_w: int,
    frame_h: int,
    mapping: list[dict[str, Any]],
    scale_from: set[str] | None = None,
    overhead: set[str] | None = None,
) -> tuple[int, int]:
    """Process all source images in directory mode.

    Two-pass approach:
      Pass 1 — Load every animation, crop frames, record dimensions.
      Pass 2 — Compute ONE global scale from the largest non-death
               crop, then apply it to every animation. The tallest
               animation fills the frame; shorter ones get natural
               headroom. Death is scaled independently.

    Args:
        source_dir: Directory containing AI source PNGs.
        output_dir: Directory for output sprite sheets.
        frame_w: Width of each frame.
        frame_h: Height of each frame.
        mapping: List of dicts with 'source', 'target', 'frames' keys.

    Returns:
        Tuple of (successes, failures).
    """
    # ------------------------------------------------------------------
    # Pass 1: load, chroma-remove, detect, crop
    # ------------------------------------------------------------------
    animations: list[dict[str, Any]] = []
    failures = 0

    for entry in mapping:
        source_path = source_dir / entry["source"]
        output_path = output_dir / entry["target"]
        expected_frames = entry["frames"]
        is_death = "death" in entry["source"].lower()

        if not source_path.exists():
            log.error("Source not found: %s", source_path)
            failures += 1
            continue

        log.info(
            "Loading: %s (%d frames expected)",
            source_path.name, expected_frames,
        )

        img = np.array(Image.open(source_path))
        rgba = remove_green_background(img)
        cleaned = _remove_small_components(rgba, min_area=5000)

        mask = cleaned[:, :, 3] > 0
        labeled, n_features = ndimage.label(mask)

        regions: list[tuple[int, int, int, int, int]] = []
        for region_id in range(1, n_features + 1):
            ys, xs = np.where(labeled == region_id)
            area = len(ys)
            if area < 5000:
                continue
            x0 = int(xs.min())
            x1 = int(xs.max()) + 1
            y0 = int(ys.min())
            y1 = int(ys.max()) + 1
            regions.append((x0, y0, x1, y1, area))

        regions.sort(key=lambda r: r[0])
        bboxes = [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in regions]

        log.info("  Detected %d sprite regions", len(bboxes))

        if len(bboxes) == 0:
            log.error("  No sprite regions found in %s", source_path.name)
            failures += 1
            continue

        frame_count = min(len(bboxes), expected_frames)

        cropped_frames = []
        for i in range(frame_count):
            cropped = _crop_region(cleaned, bboxes[i])
            cropped = _clean_green_fringe(cropped)
            cropped_frames.append(cropped)

        while len(cropped_frames) < expected_frames:
            cropped_frames.append(cropped_frames[-1].copy())

        animations.append({
            "entry": entry,
            "output_path": output_path,
            "is_death": is_death,
            "cropped_frames": cropped_frames,
        })

    # ------------------------------------------------------------------
    # Normalize body heights: idle defines the reference body size.
    # Animations shorter than idle get scaled UP to match.
    # Animations taller (overhead content) keep their size.
    # ------------------------------------------------------------------
    reference_h = 0
    reference_w = 0
    for anim in animations:
        if anim["is_death"]:
            continue
        if "idle" in anim["entry"]["source"].lower():
            reference_h = max(c.shape[0] for c in anim["cropped_frames"])
            reference_w = max(c.shape[1] for c in anim["cropped_frames"])
            break

    if reference_h == 0:
        for anim in animations:
            if not anim["is_death"]:
                reference_h = max(c.shape[0] for c in anim["cropped_frames"])
                reference_w = max(c.shape[1] for c in anim["cropped_frames"])
                break

    log.info("")
    log.info("Reference body: %dx%d (from idle)", reference_w, reference_h)

    for anim in animations:
        is_crouch = "crouch" in anim["entry"]["source"].lower()
        if anim["is_death"]:
            anim["pre_scale"] = 1.0
            continue
        if is_crouch:
            max_w = max(c.shape[1] for c in anim["cropped_frames"])
            anim["pre_scale"] = reference_w / max_w
            log.info(
                "  %s: crouch width-normalize %.4f (width %d -> %d to match idle)",
                anim["entry"]["source"], anim["pre_scale"], max_w, reference_w,
            )
            continue
        src_name = anim["entry"]["source"]
        max_h = max(c.shape[0] for c in anim["cropped_frames"])
        has_overhead = overhead and src_name in overhead
        if max_h < reference_h:
            anim["pre_scale"] = reference_h / max_h
            log.info(
                "  %s: pre-scale %.4f (crop %d -> %d to match idle)",
                src_name, anim["pre_scale"], max_h, reference_h,
            )
        elif max_h > reference_h and not has_overhead:
            anim["pre_scale"] = reference_h / max_h
            log.info(
                "  %s: pre-scale %.4f (crop %d -> %d to match idle)",
                src_name, anim["pre_scale"], max_h, reference_h,
            )
        else:
            anim["pre_scale"] = 1.0
            if has_overhead:
                log.info("  %s: overhead, keeping original size", src_name)

    # ------------------------------------------------------------------
    # Compute global scale from normalized dimensions
    # ------------------------------------------------------------------
    global_max_w = 0.0
    global_max_h = 0.0
    for anim in animations:
        if anim["is_death"]:
            continue
        src_name = anim["entry"]["source"]
        if scale_from and src_name not in scale_from:
            continue
        ps = anim["pre_scale"]
        for crop in anim["cropped_frames"]:
            global_max_w = max(global_max_w, crop.shape[1] * ps)
            global_max_h = max(global_max_h, crop.shape[0] * ps)

    usable_w = max(1, frame_w - 2)
    usable_h = max(1, frame_h - 2)

    if global_max_w > 0 and global_max_h > 0:
        global_scale = min(usable_w / global_max_w, usable_h / global_max_h)
    else:
        global_scale = 1.0

    log.info(
        "Global scale: %.4f (from normalized max %.0fx%.0f into %dx%d)",
        global_scale, global_max_w, global_max_h, frame_w, frame_h,
    )
    log.info("")

    # ------------------------------------------------------------------
    # Pass 2: scale (pre_scale * global_scale) and save
    # ------------------------------------------------------------------
    successes = 0

    for anim in animations:
        entry = anim["entry"]
        output_path = anim["output_path"]
        is_death = anim["is_death"]
        cropped_frames = anim["cropped_frames"]

        if is_death:
            max_w = max(c.shape[1] for c in cropped_frames)
            max_h = max(c.shape[0] for c in cropped_frames)
            scale = min(usable_w / max_w, usable_h / max_h)
            log.info(
                "Saving: %s (death, own scale %.4f)",
                output_path.name, scale,
            )
        else:
            scale = anim["pre_scale"] * global_scale
            log.info(
                "Saving: %s (scale %.4f = pre %.4f * global %.4f)",
                output_path.name, scale, anim["pre_scale"], global_scale,
            )

        frames = []
        for i, cropped in enumerate(cropped_frames):
            framed = _scale_to_frame_uniform(
                cropped, frame_w, frame_h, scale, is_death=is_death,
            )
            frames.append(framed)
            sh, sw = cropped.shape[:2]
            log.info(
                "    Frame %d: %dx%d -> %dx%d in %dx%d",
                i + 1, sw, sh,
                max(1, int(sw * scale)), max(1, int(sh * scale)),
                frame_w, frame_h,
            )

        total_w = frame_w * len(frames)
        sheet = np.zeros((frame_h, total_w, 4), dtype=np.uint8)
        for i, frame in enumerate(frames):
            sheet[:, i * frame_w:(i + 1) * frame_w] = frame

        output_path.parent.mkdir(parents=True, exist_ok=True)
        out_img = Image.fromarray(sheet, "RGBA")
        out_img.save(str(output_path))

        log.info("  Saved: %s (%dx%d)", output_path.name, total_w, frame_h)
        successes += 1

    return successes, failures


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Process AI source images via directory+mapping or config mode."""
    args = sys.argv[1:]

    # Detect directory mode: first arg is a path (not --flag or .json config)
    is_dir_mode = (
        len(args) >= 2
        and not args[0].startswith("--")
        and not args[0].endswith(".json")
    )

    if is_dir_mode:
        _main_directory_mode(args)
    else:
        _main_config_mode(args)


def _main_directory_mode(args: list[str]) -> None:
    """Handle directory mode: <source_dir> <output_dir> --mapping ..."""
    source_dir = Path(args[0])
    output_dir = Path(args[1])
    frame_w = 48
    frame_h = 64
    mapping_strs: list[str] = []
    scale_from_strs: list[str] = []
    overhead_strs: list[str] = []

    i = 2
    while i < len(args):
        if args[i] == "--frame-width":
            frame_w = int(args[i + 1])
            i += 2
        elif args[i] == "--frame-height":
            frame_h = int(args[i + 1])
            i += 2
        elif args[i] == "--mapping":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                mapping_strs.append(args[i])
                i += 1
        elif args[i] == "--scale-from":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                scale_from_strs.append(args[i])
                i += 1
        elif args[i] == "--overhead":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                overhead_strs.append(args[i])
                i += 1
        else:
            i += 1

    if not mapping_strs:
        log.error("No --mapping provided. Usage:")
        log.error(
            "  process_ai_sprites.py <src_dir> <out_dir> "
            "--frame-width 48 --frame-height 64 "
            "--mapping idle:4 walk:6 ..."
        )
        sys.exit(1)

    mapping = parse_mapping(mapping_strs)

    if not source_dir.is_absolute():
        source_dir = PROJECT_ROOT / source_dir
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    log.info("AI Sprite Processor (directory mode)")
    log.info("  Source: %s", source_dir)
    log.info("  Output: %s", output_dir)
    log.info("  Frame size: %dx%d", frame_w, frame_h)
    log.info("  Mapping: %d entries", len(mapping))
    log.info("")

    scale_from: set[str] | None = None
    if scale_from_strs:
        scale_from = {f"{s}.png" for s in scale_from_strs}
        log.info("  Scale from: %s", ", ".join(sorted(scale_from)))

    overhead_set: set[str] | None = None
    if overhead_strs:
        overhead_set = {f"{s}.png" for s in overhead_strs}
        log.info("  Overhead: %s", ", ".join(sorted(overhead_set)))

    successes, failures = process_directory(
        source_dir=source_dir,
        output_dir=output_dir,
        frame_w=frame_w,
        frame_h=frame_h,
        mapping=mapping,
        scale_from=scale_from,
        overhead=overhead_set,
    )

    log.info("")
    log.info("Done: %d succeeded, %d failed", successes, failures)

    if failures:
        sys.exit(1)


def _main_config_mode(args: list[str]) -> None:
    """Handle config mode: <config.json> or --config-inline."""
    config_path = None
    inline = None

    i = 0
    while i < len(args):
        if args[i] == "--config-inline":
            inline = args[i + 1]
            i += 2
        else:
            config_path = args[i]
            i += 1

    if not config_path and not inline:
        default_config = PROJECT_ROOT / "tools" / "process_all_sprites_config.json"
        if default_config.exists():
            config_path = str(default_config)
        else:
            log.error("No config specified. Usage:")
            log.error("  process_ai_sprites.py <config.json>")
            log.error("  process_ai_sprites.py --config-inline '{\"sources\": [...]}'")
            log.error("  process_ai_sprites.py <src_dir> <out_dir> --mapping idle:4 ...")
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
