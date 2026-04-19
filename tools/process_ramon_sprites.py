"""Process AI-generated Ramon sprite image into game-ready sprite sheets.

Takes a single AI image with character poses on a green (#00FF00)
background and produces individual sprite sheets for each animation:
idle (4 frames), walk (8 frames), jump (2), wall_slide (2),
wall_jump (2), sling (3).

The AI image contains 9 actual poses (the jump descending and wall
slide were not generated).  These are synthesized from existing poses:
- Jump descending: derived from jump ascending with a 1px shift.
- Wall slide: derived from the idle pose, horizontally flipped.

Usage:
    conda activate safona
    python tools/process_ramon_sprites.py [input_image]

Defaults:
    input:  assets/ai_sources/ramon/image.png
    output: assets/sprites/ramon/
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRAME_W = 24
FRAME_H = 32
TARGET_HEIGHT = 30  # Idle pose scaled to ~30px tall

# Density threshold to distinguish real body pixels from thin sling
# cord artifacts when splitting merged regions.
_BODY_DENSITY_THRESHOLD = 20


def remove_green_background(arr: np.ndarray) -> np.ndarray:
    """Remove green chroma-key background and return RGBA array.

    Green pixels are detected where g-r > 40, g-b > 40, and g > 80.
    Non-green pixels get full alpha; green pixels become transparent.

    Args:
        arr: Input image as numpy array (H, W, 3 or 4).

    Returns:
        RGBA numpy array with green pixels made transparent.
    """
    if arr.shape[2] == 4:
        rgb = arr[:, :, :3]
    else:
        rgb = arr

    r = rgb[:, :, 0].astype(np.int32)
    g = rgb[:, :, 1].astype(np.int32)
    b = rgb[:, :, 2].astype(np.int32)

    is_green = (g - r > 40) & (g - b > 40) & (rgb[:, :, 1] > 80)

    rgba = np.zeros((*arr.shape[:2], 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = np.where(is_green, 0, 255)

    return rgba


def find_pose_regions(rgba: np.ndarray, min_width: int = 10) -> list[tuple[int, int, int, int]]:
    """Detect individual pose bounding boxes by finding vertical gaps.

    Scans column-wise alpha to find contiguous non-transparent regions
    separated by fully transparent columns.

    Args:
        rgba: RGBA image array with green removed.
        min_width: Minimum region width to be considered a pose.

    Returns:
        List of (x0, y0, x1, y1) bounding boxes for each pose.
    """
    alpha = rgba[:, :, 3]
    col_has_content = np.any(alpha > 0, axis=0)

    regions: list[tuple[int, int]] = []
    in_region = False
    start_x = 0

    for x in range(len(col_has_content)):
        if col_has_content[x] and not in_region:
            start_x = x
            in_region = True
        elif not col_has_content[x] and in_region:
            if x - start_x >= min_width:
                regions.append((start_x, x))
            in_region = False

    if in_region and len(col_has_content) - start_x >= min_width:
        regions.append((start_x, len(col_has_content)))

    bboxes = []
    for x0, x1 in regions:
        region_alpha = alpha[:, x0:x1]
        row_has_content = np.any(region_alpha > 0, axis=1)
        ys = np.where(row_has_content)[0]
        if len(ys) == 0:
            continue
        y0, y1 = int(ys[0]), int(ys[-1]) + 1
        bboxes.append((x0, y0, x1, y1))

    return bboxes


def split_wide_region_by_density(
    rgba: np.ndarray,
    bbox: tuple[int, int, int, int],
    threshold: int = _BODY_DENSITY_THRESHOLD,
    min_body_width: int = 30,
) -> list[tuple[int, int, int, int]]:
    """Split a wide merged region into sub-poses using column density.

    Uses a density threshold to find contiguous body-width spans of
    significant pixel content, ignoring thin connecting elements like
    sling cords.

    Args:
        rgba: Full RGBA image array.
        bbox: Bounding box of the merged region (x0, y0, x1, y1).
        threshold: Minimum column density to be considered body content.
        min_body_width: Minimum width for a sub-region to be kept.

    Returns:
        List of (x0, y0, x1, y1) bounding boxes for each sub-pose.
    """
    x0, y0, x1, y1 = bbox
    alpha = rgba[:, :, 3]
    col_density = np.sum(alpha[y0:y1, x0:x1] > 0, axis=0).astype(float)

    bodies: list[tuple[int, int]] = []
    in_body = False
    start = 0

    for j in range(len(col_density)):
        if col_density[j] >= threshold and not in_body:
            start = j
            in_body = True
        elif col_density[j] < threshold and in_body:
            if j - start >= min_body_width:
                bodies.append((start + x0, j + x0))
            in_body = False

    if in_body and len(col_density) - start >= min_body_width:
        bodies.append((start + x0, len(col_density) + x0))

    result = []
    for bx0, bx1 in bodies:
        sub_alpha = alpha[y0:y1, bx0:bx1]
        rows = np.any(sub_alpha > 0, axis=1)
        ys = np.where(rows)[0]
        if len(ys) == 0:
            continue
        by0 = y0 + int(ys[0])
        by1 = y0 + int(ys[-1]) + 1
        result.append((bx0, by0, bx1, by1))

    return result


def crop_pose(rgba: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """Crop a single pose from the full image.

    Trims any transparent border around the pose.

    Args:
        rgba: Full RGBA image array.
        bbox: (x0, y0, x1, y1) bounding box.

    Returns:
        Tightly cropped RGBA array of the pose.
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


def compute_scale_factor(idle_pose: np.ndarray) -> float:
    """Compute uniform scale factor based on idle pose height.

    Args:
        idle_pose: Cropped RGBA array of the idle standing pose.

    Returns:
        Scale factor to apply to all poses.
    """
    h = idle_pose.shape[0]
    return TARGET_HEIGHT / h


def scale_pose(pose: np.ndarray, scale: float) -> np.ndarray:
    """Scale a pose uniformly using nearest-neighbor interpolation.

    Args:
        pose: RGBA numpy array of the pose.
        scale: Scale factor.

    Returns:
        Scaled RGBA numpy array.
    """
    pil = Image.fromarray(pose, "RGBA")
    new_w = max(1, int(pose.shape[1] * scale))
    new_h = max(1, int(pose.shape[0] * scale))
    pil = pil.resize((new_w, new_h), Image.NEAREST)
    return np.array(pil)


def hard_threshold_alpha(rgba: np.ndarray, threshold: int = 100) -> np.ndarray:
    """Apply hard alpha threshold: below threshold = 0, above = 255.

    Args:
        rgba: RGBA numpy array.
        threshold: Alpha cutoff value.

    Returns:
        Modified RGBA array with binary alpha.
    """
    result = rgba.copy()
    result[:, :, 3] = np.where(result[:, :, 3] < threshold, 0, 255)
    return result


def place_in_frame(
    pose: np.ndarray,
    frame_w: int = FRAME_W,
    frame_h: int = FRAME_H,
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
    ph, pw = pose.shape[:2]

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


def synthesize_jump_descending(jump_asc: np.ndarray) -> np.ndarray:
    """Synthesize a jump-descending frame from the ascending pose.

    Shifts the lower body 1px down to convey a more extended falling
    posture.

    Args:
        jump_asc: 24x32 RGBA frame of jump ascending pose.

    Returns:
        24x32 RGBA frame for jump descending.
    """
    h, w = jump_asc.shape[:2]
    result = np.zeros_like(jump_asc)

    # Shift entire sprite 1px down (feet drop, head clips).
    result[1:] = jump_asc[:-1]

    return result


def synthesize_wall_slide(idle_frame: np.ndarray) -> np.ndarray:
    """Synthesize a wall-slide frame from the idle pose.

    Flips the idle pose horizontally (wall slide faces left) and shifts
    it 1px up to suggest being pressed against a wall.

    Args:
        idle_frame: 24x32 RGBA frame of the idle standing pose.

    Returns:
        24x32 RGBA frame for wall slide.
    """
    # Flip horizontally so the character faces left.
    flipped = idle_frame[:, ::-1].copy()

    # Shift 1px up to suggest upward press against wall.
    result = np.zeros_like(flipped)
    result[:-1] = flipped[1:]

    return result


def build_idle_sheet(idle_frame: np.ndarray) -> np.ndarray:
    """Build 4-frame idle breathing animation from a single pose.

    Frames 0 and 2 are the original. Frames 1 and 3 shift the upper
    body 1px up and down respectively to simulate breathing.
    The waist line is at ~62% from the top of the frame.

    Args:
        idle_frame: Single 24x32 RGBA frame.

    Returns:
        RGBA array of size (32, 96, 4) with 4 frames side by side.
    """
    h, w = idle_frame.shape[:2]
    waist = int(h * 0.62)

    f0 = idle_frame.copy()

    # Frame 1: upper body shifted 1px up (breathing in).
    f1 = idle_frame.copy()
    upper = idle_frame[:waist].copy()
    f1[:waist] = 0
    if waist >= 2:
        f1[:waist - 1] = upper[1:]

    f2 = idle_frame.copy()

    # Frame 3: upper body shifted 1px down (breathing out).
    f3 = idle_frame.copy()
    upper = idle_frame[:waist].copy()
    f3[:waist] = 0
    f3[1:waist] = upper[:waist - 1]

    sheet = np.zeros((h, w * 4, 4), dtype=np.uint8)
    sheet[:, 0:w] = f0
    sheet[:, w:2 * w] = f1
    sheet[:, 2 * w:3 * w] = f2
    sheet[:, 3 * w:4 * w] = f3
    return sheet


def build_walk_sheet(walk_frames: list[np.ndarray]) -> np.ndarray:
    """Build 8-frame walk cycle from 4 base poses.

    Uses cycle: [0, 1, 2, 3, 2, 1, 0, 1] for smooth back-and-forth
    leg motion.

    Args:
        walk_frames: List of 4 RGBA frames (24x32 each).

    Returns:
        RGBA array of size (32, 192, 4) with 8 frames.
    """
    cycle = [0, 1, 2, 3, 2, 1, 0, 1]
    h, w = walk_frames[0].shape[:2]
    sheet = np.zeros((h, w * len(cycle), 4), dtype=np.uint8)

    for i, idx in enumerate(cycle):
        sheet[:, i * w:(i + 1) * w] = walk_frames[idx]

    return sheet


def build_jump_sheet(asc_frame: np.ndarray, desc_frame: np.ndarray) -> np.ndarray:
    """Build 2-frame jump sheet (ascending, descending).

    Args:
        asc_frame: Jump ascending RGBA frame.
        desc_frame: Jump descending RGBA frame.

    Returns:
        RGBA array of size (32, 48, 4).
    """
    h, w = asc_frame.shape[:2]
    sheet = np.zeros((h, w * 2, 4), dtype=np.uint8)
    sheet[:, 0:w] = asc_frame
    sheet[:, w:2 * w] = desc_frame
    return sheet


def build_wall_slide_sheet(ws_frame: np.ndarray) -> np.ndarray:
    """Build 2-frame wall slide sheet with 1px vertical shift variation.

    Args:
        ws_frame: Single 24x32 RGBA frame.

    Returns:
        RGBA array of size (32, 48, 4) with 2 frames.
    """
    h, w = ws_frame.shape[:2]
    f0 = ws_frame.copy()

    # Frame 1: shift entire sprite 1px down for subtle movement.
    f1 = np.zeros_like(ws_frame)
    f1[1:] = ws_frame[:-1]

    sheet = np.zeros((h, w * 2, 4), dtype=np.uint8)
    sheet[:, 0:w] = f0
    sheet[:, w:2 * w] = f1
    return sheet


def build_wall_jump_sheet(jump_asc_frame: np.ndarray) -> np.ndarray:
    """Build 2-frame wall jump sheet from jump ascending pose.

    Frame 0 is the ascending pose. Frame 1 shifts upper body 1px up.

    Args:
        jump_asc_frame: Single 24x32 RGBA frame (jump ascending).

    Returns:
        RGBA array of size (32, 48, 4) with 2 frames.
    """
    h, w = jump_asc_frame.shape[:2]
    f0 = jump_asc_frame.copy()

    f1 = jump_asc_frame.copy()
    waist = int(h * 0.62)
    upper = jump_asc_frame[:waist].copy()
    f1[:waist] = 0
    if waist >= 2:
        f1[:waist - 1] = upper[1:]

    sheet = np.zeros((h, w * 2, 4), dtype=np.uint8)
    sheet[:, 0:w] = f0
    sheet[:, w:2 * w] = f1
    return sheet


def build_sling_sheet(sling_frames: list[np.ndarray]) -> np.ndarray:
    """Build 3-frame sling sheet (wind-up, mid-rotation, release).

    Args:
        sling_frames: List of 3 RGBA frames (24x32 each).

    Returns:
        RGBA array of size (32, 72, 4).
    """
    h, w = sling_frames[0].shape[:2]
    sheet = np.zeros((h, w * len(sling_frames), 4), dtype=np.uint8)

    for i, frame in enumerate(sling_frames):
        sheet[:, i * w:(i + 1) * w] = frame

    return sheet


def save_sheet(sheet: np.ndarray, path: Path) -> None:
    """Save an RGBA sheet as a PNG file.

    Args:
        sheet: RGBA numpy array.
        path: Output file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(sheet, "RGBA")
    img.save(str(path))
    print(f"  Saved: {path} ({sheet.shape[1]}x{sheet.shape[0]})")


def main() -> None:
    """Process the AI image and generate all sprite sheets.

    Detects 7 top-level regions in the image, splits the wide merged
    rightmost region by column density to extract sling sub-poses,
    yielding 9 total poses:

        0: idle, 1-4: walk frames, 5: jump ascending,
        6: sling wind-up, 7: sling mid-rotation, 8: sling release.

    Jump descending and wall slide are synthesized from existing poses.
    """
    input_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else PROJECT_ROOT / "assets" / "ai_sources" / "ramon" / "image.png"
    )
    output_dir = PROJECT_ROOT / "assets" / "sprites" / "ramon"

    print(f"Input: {input_path}")
    print(f"Output: {output_dir}/")

    # Load and remove green background.
    img = np.array(Image.open(input_path))
    print(f"Image size: {img.shape[1]}x{img.shape[0]}")

    rgba = remove_green_background(img)
    print("Green removal complete")

    # Detect top-level regions (separated by fully transparent columns).
    raw_regions = find_pose_regions(rgba)
    print(f"Found {len(raw_regions)} top-level regions")

    # Split wide merged regions by density.
    # Regions with width > 200 likely contain multiple poses connected
    # by thin sling cords.
    all_poses: list[tuple[int, int, int, int]] = []
    for bbox in raw_regions:
        x0, _, x1, _ = bbox
        width = x1 - x0
        if width > 200:
            sub_poses = split_wide_region_by_density(rgba, bbox)
            print(f"  Split wide region (x={x0}..{x1}, w={width}) "
                  f"into {len(sub_poses)} sub-poses")
            all_poses.extend(sub_poses)
        else:
            all_poses.append(bbox)

    print(f"Total poses detected: {len(all_poses)}")
    for i, (x0, y0, x1, y1) in enumerate(all_poses):
        print(f"  Pose {i}: x=[{x0}..{x1}] w={x1 - x0} "
              f"y=[{y0}..{y1}] h={y1 - y0}")

    if len(all_poses) < 9:
        print(f"ERROR: Expected at least 9 poses, found {len(all_poses)}.")
        sys.exit(1)

    # Crop all poses tightly.
    poses = [crop_pose(rgba, bb) for bb in all_poses]

    # Compute scale factor from idle pose (pose 0).
    scale = compute_scale_factor(poses[0])
    print(f"Scale factor: {scale:.4f} "
          f"(idle height {poses[0].shape[0]}px -> {TARGET_HEIGHT}px)")

    # Scale all poses.
    scaled = [scale_pose(p, scale) for p in poses]

    # Hard-threshold alpha.
    scaled = [hard_threshold_alpha(p) for p in scaled]

    # Place each pose in a 24x32 frame.
    framed = [place_in_frame(p) for p in scaled]

    for i, f in enumerate(framed):
        print(f"  Framed pose {i}: {f.shape[1]}x{f.shape[0]}")

    # Assign poses to animation roles.
    # Poses: 0=idle, 1-4=walk, 5=jump_asc, 6=sling_windup,
    #         7=sling_mid, 8=sling_release
    idle = framed[0]
    walk_a, walk_b, walk_c, walk_d = framed[1], framed[2], framed[3], framed[4]
    jump_asc = framed[5]
    sling_windup = framed[6]
    sling_mid = framed[7]
    sling_release = framed[8]

    # Synthesize missing poses.
    jump_desc = synthesize_jump_descending(jump_asc)
    wall_slide = synthesize_wall_slide(idle)

    print("\nBuilding sprite sheets...")

    # Idle: 4 frames with breathing bob.
    idle_sheet = build_idle_sheet(idle)
    save_sheet(idle_sheet, output_dir / "idle.png")

    # Walk: 4 base frames -> 8-frame cycle.
    walk_sheet = build_walk_sheet([walk_a, walk_b, walk_c, walk_d])
    save_sheet(walk_sheet, output_dir / "walk.png")

    # Jump: ascending + descending (synthesized).
    jump_sheet = build_jump_sheet(jump_asc, jump_desc)
    save_sheet(jump_sheet, output_dir / "jump.png")

    # Wall slide: synthesized from idle, 2 frames with variation.
    wall_slide_sheet = build_wall_slide_sheet(wall_slide)
    save_sheet(wall_slide_sheet, output_dir / "wall_slide.png")

    # Wall jump: from jump ascending, 2 frames with variation.
    wall_jump_sheet = build_wall_jump_sheet(jump_asc)
    save_sheet(wall_jump_sheet, output_dir / "wall_jump.png")

    # Sling: 3 frames (wind-up, mid-rotation, release).
    sling_sheet = build_sling_sheet([sling_windup, sling_mid, sling_release])
    save_sheet(sling_sheet, output_dir / "sling.png")

    print("\nDone! All sprite sheets generated.")


if __name__ == "__main__":
    main()
