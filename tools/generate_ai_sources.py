"""Generate placeholder AI source images for tilesets, backgrounds, and UI.

Since AI-generated source images don't exist yet, this script creates
programmatic placeholders that mimic what the AI sources would look like:
tiles on green backgrounds, scenic backgrounds, and UI elements.

Usage:
    python tools/generate_ai_sources.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Green background color for sprites/tiles
GREEN_BG = (0, 200, 0)


def _draw_stone_tile(draw: ImageDraw.Draw, x: int, y: int, size: int,
                     base_color: tuple, mortar_color: tuple,
                     has_grass: bool = False, grass_color: tuple = (80, 130, 60)) -> None:
    """Draw a single stone tile with detail."""
    rng = np.random.RandomState(hash((x, y, base_color[0])) % (2**31))

    # Fill base
    draw.rectangle([x, y, x + size - 1, y + size - 1], fill=base_color)

    # Mortar lines
    for my in range(y + size // 4, y + size, size // 4):
        draw.line([(x + 2, my), (x + size - 3, my)], fill=mortar_color, width=1)
    for mx in range(x + size // 3, x + size, size // 3):
        draw.line([(mx, y + 2), (mx, y + size - 3)], fill=mortar_color, width=1)

    # Random cracks/texture
    for _ in range(3):
        cx = x + rng.randint(4, size - 4)
        cy = y + rng.randint(4, size - 4)
        r = max(0, base_color[0] - 20 + rng.randint(-10, 10))
        g = max(0, base_color[1] - 20 + rng.randint(-10, 10))
        b = max(0, base_color[2] - 20 + rng.randint(-10, 10))
        draw.point((cx, cy), fill=(r, g, b))

    # Grass on top
    if has_grass:
        for gx in range(x, x + size, 2):
            gh = rng.randint(3, 8)
            g_r = grass_color[0] + rng.randint(-15, 15)
            g_g = grass_color[1] + rng.randint(-15, 15)
            g_b = grass_color[2] + rng.randint(-15, 15)
            draw.line([(gx, y), (gx, y + gh)],
                      fill=(max(0, min(255, g_r)),
                            max(0, min(255, g_g)),
                            max(0, min(255, g_b))), width=1)


def generate_tileset_source(output_path: Path, palette: str = "warm") -> None:
    """Generate a 4-tile source image on green background.

    Args:
        output_path: Where to save the image.
        palette: 'warm' for stone, 'cave' for cool cave, 'talayot' for ancient.
    """
    tile_size = 256
    margin = 80
    img_w = tile_size * 4 + margin * 5
    img_h = tile_size + margin * 2
    img = Image.new("RGB", (img_w, img_h), GREEN_BG)
    draw = ImageDraw.Draw(img)

    if palette == "cave":
        base_colors = [
            (90, 95, 105),   # top surface (with moss)
            (80, 85, 95),    # inner stone
            (55, 58, 65),    # underground (darker)
            (75, 80, 90),    # wall edge
        ]
        mortar = (60, 63, 72)
        grass_color = (50, 90, 70)  # Moss/damp tint
    elif palette == "talayot":
        base_colors = [
            (170, 145, 110),  # top surface (warm ancient)
            (150, 128, 95),   # inner stone
            (110, 92, 68),    # underground
            (140, 118, 88),   # wall edge
        ]
        mortar = (120, 100, 72)
        grass_color = (90, 120, 55)  # Sparse dry grass
    else:  # warm (default world1)
        base_colors = [
            (180, 165, 130),  # top surface
            (165, 148, 115),  # inner stone
            (120, 105, 80),   # underground
            (155, 138, 105),  # wall edge
        ]
        mortar = (140, 125, 95)
        grass_color = (80, 130, 60)

    has_grass = [True, False, False, False]

    for i in range(4):
        tx = margin + i * (tile_size + margin)
        ty = margin
        _draw_stone_tile(draw, tx, ty, tile_size, base_colors[i], mortar,
                         has_grass=has_grass[i], grass_color=grass_color)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"Generated: {output_path} ({img.size[0]}x{img.size[1]})")


def generate_background(output_path: Path, theme: str = "outdoor") -> None:
    """Generate a scenic background image at 384x216.

    Args:
        output_path: Where to save.
        theme: 'outdoor', 'cave', or 'talayot'.
    """
    w, h = 384, 216
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    if theme == "cave":
        # Dark cave background with stalactites
        for y in range(h):
            t = y / h
            r = int(25 + t * 15)
            g = int(30 + t * 15)
            b = int(45 + t * 10)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        # Stalactites from ceiling
        rng = np.random.RandomState(42)
        for _ in range(15):
            sx = rng.randint(0, w)
            sl = rng.randint(15, 50)
            sw = rng.randint(3, 8)
            color = (50 + rng.randint(0, 20), 55 + rng.randint(0, 20), 65 + rng.randint(0, 20))
            draw.polygon([(sx - sw, 0), (sx + sw, 0), (sx, sl)], fill=color)
        # Dim glow spots
        for _ in range(5):
            gx = rng.randint(20, w - 20)
            gy = rng.randint(20, h - 20)
            for r in range(12, 0, -1):
                alpha = int(15 * (12 - r) / 12)
                color = (40 + alpha, 60 + alpha, 80 + alpha * 2)
                draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=color)
    elif theme == "talayot":
        # Ancient warm interior with stone walls
        for y in range(h):
            t = y / h
            r = int(100 + t * 40)
            g = int(80 + t * 35)
            b = int(55 + t * 25)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        # Ancient stone block pattern in background
        rng = np.random.RandomState(123)
        block_h = 20
        block_w = 30
        for by in range(0, h, block_h):
            offset = (by // block_h % 2) * (block_w // 2)
            for bx in range(-block_w, w + block_w, block_w):
                x0 = bx + offset
                color_var = rng.randint(-8, 8)
                base = (90 + color_var, 75 + color_var, 55 + color_var)
                draw.rectangle([x0 + 1, by + 1, x0 + block_w - 2, by + block_h - 2],
                               fill=base, outline=(70, 58, 40))
        # Warm torchlight glow
        for tx in [80, 300]:
            for r in range(30, 0, -1):
                alpha = int(30 * (30 - r) / 30)
                color = (140 + alpha, 100 + alpha // 2, 50)
                draw.ellipse([tx - r, 40 - r, tx + r, 40 + r], fill=color)
    else:  # outdoor Mediterranean
        # Sky gradient (blue to warm)
        for y in range(h):
            t = y / h
            r = int(110 + t * 90)
            g = int(170 - t * 40)
            b = int(220 - t * 80)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        # Distant mountains
        rng = np.random.RandomState(7)
        for layer in range(3):
            points = [(0, h)]
            base_y = h - 60 + layer * 20
            for x in range(0, w + 20, 20):
                points.append((x, base_y - rng.randint(10, 40)))
            points.append((w, h))
            shade = 140 - layer * 30
            color = (shade, shade + 10, shade - 10)
            draw.polygon(points, fill=color)
        # Sea at horizon
        sea_y = int(h * 0.55)
        for y in range(sea_y, int(h * 0.7)):
            t = (y - sea_y) / (h * 0.15)
            r = int(60 + t * 30)
            g = int(120 + t * 20)
            b = int(180 - t * 20)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"Generated background: {output_path}")


def generate_ui_element(output_path: Path, element_type: str) -> None:
    """Generate a UI element on green background.

    Args:
        output_path: Where to save.
        element_type: One of 'hearts', 'stone_icon', 'mask_stone_slam',
                     'dialogue_frame', 'shop_frame', 'boss_health_bar',
                     'charge_indicator', 'game_over', 'title'.
    """
    if element_type == "hearts":
        # 3 heart states in a horizontal strip: full, half, empty
        size = 64
        margin = 20
        img_w = size * 3 + margin * 4
        img_h = size + margin * 2
        img = Image.new("RGBA", (img_w, img_h), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        colors = [(220, 40, 40), (220, 120, 120), (80, 40, 40)]
        for i, color in enumerate(colors):
            cx = margin + i * (size + margin) + size // 2
            cy = margin + size // 2
            half = size // 2 - 4
            # Diamond heart shape
            points = [(cx, cy - half), (cx + half, cy),
                      (cx, cy + half), (cx - half, cy)]
            draw.polygon(points, fill=color, outline=(max(0, color[0] - 60),
                                                       max(0, color[1] - 60),
                                                       max(0, color[2] - 60)))

    elif element_type == "stone_icon":
        size = 64
        margin = 20
        img = Image.new("RGBA", (size + margin * 2, size + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        cx, cy = margin + size // 2, margin + size // 2
        r = size // 2 - 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(160, 160, 160),
                     outline=(120, 120, 120))
        # Stone texture dots
        rng = np.random.RandomState(55)
        for _ in range(8):
            dx = rng.randint(-r + 5, r - 5)
            dy = rng.randint(-r + 5, r - 5)
            draw.point((cx + dx, cy + dy), fill=(140, 140, 140))

    elif element_type == "mask_stone_slam":
        size = 80
        margin = 20
        img = Image.new("RGBA", (size + margin * 2, size + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        cx, cy = margin + size // 2, margin + size // 2
        # Mask shape (oval with eye holes)
        draw.ellipse([cx - 30, cy - 35, cx + 30, cy + 25], fill=(180, 150, 50),
                     outline=(140, 110, 30))
        draw.ellipse([cx - 18, cy - 15, cx - 6, cy - 5], fill=(40, 30, 20))
        draw.ellipse([cx + 6, cy - 15, cx + 18, cy - 5], fill=(40, 30, 20))
        # Impact lines below
        for i in range(-2, 3):
            draw.line([(cx + i * 10, cy + 25), (cx + i * 15, cy + 38)],
                      fill=(255, 220, 80), width=2)

    elif element_type == "dialogue_frame":
        # Frame for dialogue box (372x68 at base res, but source is larger)
        fw, fh = 400, 100
        margin = 10
        img = Image.new("RGBA", (fw + margin * 2, fh + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        # Dark semi-transparent box with golden border
        draw.rectangle([margin, margin, margin + fw - 1, margin + fh - 1],
                       fill=(10, 8, 18, 245))
        draw.rectangle([margin, margin, margin + fw - 1, margin + fh - 1],
                       outline=(200, 180, 130), width=2)
        # Corner ornaments
        for cx, cy in [(margin, margin), (margin + fw - 1, margin),
                       (margin, margin + fh - 1), (margin + fw - 1, margin + fh - 1)]:
            draw.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=(200, 180, 130))

    elif element_type == "shop_frame":
        fw, fh = 300, 180
        margin = 10
        img = Image.new("RGBA", (fw + margin * 2, fh + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([margin, margin, margin + fw - 1, margin + fh - 1],
                       fill=(15, 12, 25, 240))
        draw.rectangle([margin, margin, margin + fw - 1, margin + fh - 1],
                       outline=(180, 160, 100), width=2)
        # Header area
        draw.rectangle([margin + 4, margin + 4, margin + fw - 5, margin + 24],
                       fill=(40, 30, 50))
        draw.rectangle([margin + 4, margin + 4, margin + fw - 5, margin + 24],
                       outline=(180, 160, 100), width=1)

    elif element_type == "boss_health_bar":
        bw, bh = 200, 16
        margin = 10
        img = Image.new("RGBA", (bw + margin * 2, bh + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        # Background bar
        draw.rectangle([margin, margin, margin + bw - 1, margin + bh - 1],
                       fill=(30, 10, 10), outline=(150, 40, 40), width=1)
        # Fill gradient (red to dark red)
        for x in range(bw - 4):
            t = x / max(bw - 5, 1)
            r = int(200 - t * 40)
            g = int(40 - t * 20)
            draw.line([(margin + 2 + x, margin + 2),
                       (margin + 2 + x, margin + bh - 3)], fill=(r, g, 20))

    elif element_type == "charge_indicator":
        cw, ch = 40, 12
        margin = 10
        img = Image.new("RGBA", (cw * 3 + margin * 4, ch + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        # Three charge tiers
        colors = [(180, 180, 80), (255, 180, 50), (255, 60, 60)]
        for i, color in enumerate(colors):
            x0 = margin + i * (cw + margin)
            draw.rectangle([x0, margin, x0 + cw - 1, margin + ch - 1],
                           fill=color, outline=tuple(max(0, c - 60) for c in color))

    elif element_type == "game_over":
        tw, th = 250, 120
        margin = 20
        img = Image.new("RGBA", (tw + margin * 2, th + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        # Dark background with red tint
        draw.rectangle([margin, margin, margin + tw - 1, margin + th - 1],
                       fill=(60, 15, 15))
        # "GAME OVER" text (large)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except (IOError, OSError):
            font = ImageFont.load_default()
        draw.text((margin + 20, margin + 30), "GAME OVER", fill=(220, 40, 40), font=font)

    elif element_type == "title":
        tw, th = 300, 100
        margin = 20
        img = Image.new("RGBA", (tw + margin * 2, th + margin * 2), (*GREEN_BG, 255))
        draw = ImageDraw.Draw(img)
        # Title logo background
        draw.rectangle([margin, margin, margin + tw - 1, margin + th - 1],
                       fill=(20, 20, 40))
        # "SA FONA" text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except (IOError, OSError):
            font = ImageFont.load_default()
        draw.text((margin + 30, margin + 20), "SA FONA", fill=(255, 220, 80), font=font)
    else:
        print(f"Unknown UI element type: {element_type}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"Generated UI element: {output_path}")


def main() -> None:
    """Generate all placeholder AI source images."""
    ai_dir = PROJECT_ROOT / "assets" / "ai_sources"

    # Tilesets
    generate_tileset_source(ai_dir / "tileset_world1_cave" / "image.png", palette="cave")
    generate_tileset_source(ai_dir / "tileset_world1_talayot" / "image.png", palette="talayot")

    # Backgrounds
    generate_background(ai_dir / "bg_world1" / "image.png", theme="outdoor")
    generate_background(ai_dir / "bg_world1_cave" / "image.png", theme="cave")
    generate_background(ai_dir / "bg_world1_talayot" / "image.png", theme="talayot")

    # UI elements
    ui_elements = [
        "hearts", "stone_icon", "mask_stone_slam",
        "dialogue_frame", "shop_frame", "boss_health_bar",
        "charge_indicator", "game_over", "title",
    ]
    for elem in ui_elements:
        generate_ui_element(ai_dir / f"ui_{elem}" / "image.png", elem)

    print("\nAll AI source placeholders generated.")


if __name__ == "__main__":
    main()
