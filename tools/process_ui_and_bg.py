"""Process AI-generated backgrounds and UI elements into game-ready assets.

Handles two types of assets:
1. Backgrounds: Full-screen scenic images scaled to 384x216 (game resolution).
2. UI elements: Individual sprites extracted from green background and scaled.

Usage:
    python tools/process_ui_and_bg.py

Or process individual assets:
    python tools/process_ui_and_bg.py --bg <input> <output>
    python tools/process_ui_and_bg.py --ui <input> <output> <width> <height>
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Game native resolution.
GAME_WIDTH = 384
GAME_HEIGHT = 216


def has_green_background(img_arr: np.ndarray, threshold: float = 0.2) -> bool:
    """Detect whether an image has a significant green chroma key background.

    Args:
        img_arr: Image as numpy array (H, W, 3 or 4).
        threshold: Fraction of pixels that must be green to count.

    Returns:
        True if more than `threshold` fraction of pixels are green.
    """
    if img_arr.shape[2] == 4:
        rgb = img_arr[:, :, :3]
    else:
        rgb = img_arr

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gi, ri, bi = g.astype(int), r.astype(int), b.astype(int)
    is_green = (gi - ri > 40) & (gi - bi > 40) & (g > 80)
    green_ratio = is_green.sum() / (img_arr.shape[0] * img_arr.shape[1])
    return green_ratio > threshold


def remove_green_background(img: Image.Image) -> Image.Image:
    """Remove green chroma key background, replacing with transparency.

    Args:
        img: PIL Image with potential green background.

    Returns:
        RGBA Image with green pixels made transparent.
    """
    img = img.convert("RGBA")
    arr = np.array(img)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    gi, ri, bi = g.astype(int), r.astype(int), b.astype(int)
    is_green = (gi - ri > 40) & (gi - bi > 40) & (g > 80)

    # Set alpha to 0 for green pixels.
    arr[:, :, 3] = np.where(is_green, 0, 255)

    return Image.fromarray(arr)


def extract_sprite_from_green(img: Image.Image) -> Image.Image:
    """Extract the main non-green region from an image.

    Finds the bounding box of all non-green pixels and crops to it,
    with a small padding.

    Args:
        img: PIL Image with green background.

    Returns:
        Cropped RGBA image of just the sprite content.
    """
    rgba = remove_green_background(img)
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 0)

    if len(ys) == 0:
        return rgba

    pad = 2
    y0 = max(0, ys.min() - pad)
    y1 = min(arr.shape[0], ys.max() + 1 + pad)
    x0 = max(0, xs.min() - pad)
    x1 = min(arr.shape[1], xs.max() + 1 + pad)

    return Image.fromarray(arr[y0:y1, x0:x1])


def extract_multi_sprites(img: Image.Image, min_area: int = 100) -> list[Image.Image]:
    """Extract multiple separate sprites from a green background image.

    Uses connected component labeling to find distinct non-green regions.

    Args:
        img: PIL Image with green background.
        min_area: Minimum pixel area for a valid sprite region.

    Returns:
        List of cropped RGBA images, one per sprite region.
    """
    rgba = remove_green_background(img)
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    mask = alpha > 0

    labeled, num_features = ndimage.label(mask)
    sprites: list[Image.Image] = []

    for region_id in range(1, num_features + 1):
        ys, xs = np.where(labeled == region_id)
        if len(ys) < min_area:
            continue

        pad = 2
        y0 = max(0, ys.min() - pad)
        y1 = min(arr.shape[0], ys.max() + 1 + pad)
        x0 = max(0, xs.min() - pad)
        x1 = min(arr.shape[1], xs.max() + 1 + pad)

        sprite = arr[y0:y1, x0:x1].copy()
        # Clear pixels not belonging to this region.
        region_mask = labeled[y0:y1, x0:x1] != region_id
        sprite[region_mask, 3] = 0

        sprites.append(Image.fromarray(sprite))

    return sprites


def process_background(input_path: Path, output_path: Path) -> None:
    """Process a background image: remove green BG if present, scale to game res.

    Args:
        input_path: Path to source background image.
        output_path: Path to save processed background.
    """
    img = Image.open(input_path)
    arr = np.array(img.convert("RGB"))

    if has_green_background(arr):
        # Unlikely for backgrounds but handle it.
        img = remove_green_background(img)
        # Composite onto a black background for the final result.
        bg = Image.new("RGB", img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[3])
        img = bg

    # Scale to game resolution.
    img = img.convert("RGB")
    img = img.resize((GAME_WIDTH, GAME_HEIGHT), Image.LANCZOS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"Processed background: {output_path} ({img.size[0]}x{img.size[1]})")


def process_ui_element(
    input_path: Path,
    output_path: Path,
    target_width: int,
    target_height: int,
    multi_sprite: bool = False,
) -> None:
    """Process a UI element: extract from green BG, scale to target size.

    Args:
        input_path: Path to source UI image.
        output_path: Path to save processed UI element.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        multi_sprite: If True, extract multiple sprites as horizontal strip.
    """
    img = Image.open(input_path)

    if multi_sprite:
        sprites = extract_multi_sprites(img)
        if not sprites:
            print(f"Warning: no sprites found in {input_path}")
            return

        # Scale each sprite and combine into horizontal strip.
        scaled = []
        for sprite in sprites:
            s = sprite.resize((target_width, target_height), Image.LANCZOS)
            # Sharpen for pixel art quality at small sizes.
            s = ImageEnhance.Sharpness(s).enhance(1.5)
            scaled.append(s)

        strip = Image.new("RGBA", (target_width * len(scaled), target_height), (0, 0, 0, 0))
        for i, s in enumerate(scaled):
            strip.paste(s, (i * target_width, 0))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        strip.save(str(output_path))
        print(f"Processed UI strip: {output_path} ({strip.size[0]}x{strip.size[1]}, {len(scaled)} frames)")
    else:
        sprite = extract_sprite_from_green(img)
        sprite = sprite.resize((target_width, target_height), Image.LANCZOS)
        sprite = ImageEnhance.Sharpness(sprite).enhance(1.5)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        sprite.save(str(output_path))
        print(f"Processed UI element: {output_path} ({sprite.size[0]}x{sprite.size[1]})")


def process_all() -> None:
    """Process all backgrounds and UI elements."""
    ai_dir = PROJECT_ROOT / "assets" / "ai_sources"
    bg_dir = PROJECT_ROOT / "assets" / "backgrounds"
    ui_dir = PROJECT_ROOT / "assets" / "ui"

    # Backgrounds.
    backgrounds = [
        ("bg_world1", "world1.png"),
        ("bg_world1_cave", "world1_cave.png"),
        ("bg_world1_talayot", "world1_talayot.png"),
    ]
    for source_dir, output_name in backgrounds:
        input_path = ai_dir / source_dir / "image.png"
        output_path = bg_dir / output_name
        if input_path.exists():
            process_background(input_path, output_path)
        else:
            print(f"Skip (not found): {input_path}")

    # UI elements: (source_dir, output_name, width, height, multi_sprite).
    ui_elements = [
        ("ui_hearts", "hud_heart.png", 12, 12, True),
        ("ui_stone_icon", "hud_stone.png", 12, 12, False),
        ("ui_mask_stone_slam", "mask_stone_slam.png", 16, 16, False),
        ("ui_dialogue_frame", "dialogue_frame.png", 372, 68, False),
        ("ui_shop_frame", "shop_frame.png", 280, 160, False),
        ("ui_boss_health_bar", "boss_health_bar.png", 200, 12, False),
        ("ui_charge_indicator", "charge_indicator.png", 12, 4, True),
        ("ui_game_over", "game_over.png", 200, 100, False),
        ("ui_title", "title.png", 280, 80, False),
    ]
    for source_dir, output_name, tw, th, multi in ui_elements:
        input_path = ai_dir / source_dir / "image.png"
        output_path = ui_dir / output_name
        if input_path.exists():
            process_ui_element(input_path, output_path, tw, th, multi_sprite=multi)
        else:
            print(f"Skip (not found): {input_path}")


def main() -> None:
    """Entry point: process all or individual assets based on CLI args."""
    if len(sys.argv) > 1 and sys.argv[1] == "--bg":
        if len(sys.argv) < 4:
            print("Usage: process_ui_and_bg.py --bg <input> <output>")
            sys.exit(1)
        process_background(Path(sys.argv[2]), Path(sys.argv[3]))
    elif len(sys.argv) > 1 and sys.argv[1] == "--ui":
        if len(sys.argv) < 6:
            print("Usage: process_ui_and_bg.py --ui <input> <output> <width> <height>")
            sys.exit(1)
        multi = "--multi" in sys.argv
        process_ui_element(
            Path(sys.argv[2]), Path(sys.argv[3]),
            int(sys.argv[4]), int(sys.argv[5]),
            multi_sprite=multi,
        )
    else:
        process_all()


if __name__ == "__main__":
    main()
