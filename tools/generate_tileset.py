"""World 1 tileset generator for Sa Fona.

Generates a 16-tile auto-tile strip (256x16 PNG) where each tile
corresponds to a 4-bit neighbor bitmask:

    UP=1, DOWN=2, LEFT=4, RIGHT=8

Index 0  = isolated block (no solid neighbors)
Index 14 = top surface (down+left+right solid, up open) — grassy
Index 15 = inner block (all neighbors solid) — pure stone

Mediterranean stone palette with grass on exposed tops and
darker edges on exposed sides.

Usage:
    conda activate safona
    python tools/generate_tileset.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TILE_SIZE = 16
NUM_TILES = 16

UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8

# ── Palette ──────────────────────────────────────────────────

STONE_COLORS = [
    (195, 170, 130, 255),  # base
    (210, 185, 145, 255),  # light
    (180, 155, 118, 255),  # mid
    (168, 145, 108, 255),  # dark
]
STONE_EDGE = (145, 125, 92, 255)
STONE_EDGE_DARK = (130, 112, 82, 255)

GRASS_COLORS = [
    (88, 128, 62, 255),    # base
    (105, 145, 75, 255),   # light
    (72, 108, 50, 255),    # dark
]
GRASS_TIP = (120, 155, 85, 255)

DIRT = (160, 128, 82, 255)
DIRT_DARK = (142, 112, 70, 255)


def _stone_texture(seed: int) -> Image.Image:
    """Generate a 16x16 stone texture with subtle variation."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), STONE_COLORS[0])
    px = img.load()

    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            r = rng.random()
            if r < 0.25:
                px[x, y] = STONE_COLORS[1]
            elif r < 0.45:
                px[x, y] = STONE_COLORS[2]
            elif r < 0.55:
                px[x, y] = STONE_COLORS[3]

    # Horizontal mortar lines every 5-6 rows
    for y in [5, 11]:
        for x in range(TILE_SIZE):
            if rng.random() < 0.85:
                px[x, y] = STONE_COLORS[3]

    # Vertical mortar offsets
    for x in [4, 12]:
        for y in range(0, 5):
            if rng.random() < 0.6:
                px[x, y] = STONE_COLORS[3]
    for x in [8]:
        for y in range(6, 11):
            if rng.random() < 0.6:
                px[x, y] = STONE_COLORS[3]

    return img


def _add_grass_top(img: Image.Image, seed: int) -> None:
    """Add grass and dirt to the top of a tile (exposed top edge)."""
    rng = random.Random(seed)
    px = img.load()

    for x in range(TILE_SIZE):
        grass_h = rng.randint(2, 4)

        # Grass tip (row 0)
        px[x, 0] = GRASS_TIP if rng.random() > 0.4 else GRASS_COLORS[1]

        # Grass body
        for y in range(1, grass_h):
            r = rng.random()
            if r < 0.4:
                px[x, y] = GRASS_COLORS[0]
            elif r < 0.7:
                px[x, y] = GRASS_COLORS[1]
            else:
                px[x, y] = GRASS_COLORS[2]

        # Dirt layer under grass
        if grass_h < TILE_SIZE:
            px[x, grass_h] = DIRT
        if grass_h + 1 < TILE_SIZE:
            px[x, grass_h + 1] = DIRT_DARK


def _add_edge(img: Image.Image, side: str) -> None:
    """Darken a 2px edge on the specified side."""
    px = img.load()
    if side == "bottom":
        for x in range(TILE_SIZE):
            px[x, TILE_SIZE - 1] = STONE_EDGE_DARK
            px[x, TILE_SIZE - 2] = STONE_EDGE
    elif side == "left":
        for y in range(TILE_SIZE):
            px[0, y] = STONE_EDGE_DARK
            px[1, y] = STONE_EDGE
    elif side == "right":
        for y in range(TILE_SIZE):
            px[TILE_SIZE - 1, y] = STONE_EDGE_DARK
            px[TILE_SIZE - 2, y] = STONE_EDGE
    elif side == "top":
        for x in range(TILE_SIZE):
            px[x, 0] = STONE_EDGE_DARK
            px[x, 1] = STONE_EDGE


def generate_tile(bitmask: int, seed: int = 42) -> Image.Image:
    """Generate a single auto-tile variant.

    Args:
        bitmask: 4-bit neighbor mask (UP|DOWN|LEFT|RIGHT).
        seed: Random seed for texture consistency.

    Returns:
        A 16x16 RGBA PIL Image.
    """
    img = _stone_texture(seed)

    has_up = bool(bitmask & UP)
    has_down = bool(bitmask & DOWN)
    has_left = bool(bitmask & LEFT)
    has_right = bool(bitmask & RIGHT)

    # Grass on exposed top (most important visual feature)
    if not has_up:
        _add_grass_top(img, seed + 1000)

    # Darker edges on exposed sides
    if not has_down:
        _add_edge(img, "bottom")
    if not has_left:
        _add_edge(img, "left")
    if not has_right:
        _add_edge(img, "right")
    if has_up and not has_down and not has_left and not has_right:
        _add_edge(img, "top")

    return img


def main() -> None:
    """Generate the World 1 tileset strip."""
    output_path = PROJECT_ROOT / "assets" / "tilesets" / "world1" / "tileset.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tileset = Image.new("RGBA", (NUM_TILES * TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))

    # Index 0 stays transparent (empty tile)
    for i in range(1, NUM_TILES):
        tile = generate_tile(i, seed=100 + i * 7)
        tileset.paste(tile, (i * TILE_SIZE, 0))

    tileset.save(str(output_path))
    print(f"Tileset: {output_path.relative_to(PROJECT_ROOT)} ({NUM_TILES * TILE_SIZE}x{TILE_SIZE}, {NUM_TILES} tiles)")


if __name__ == "__main__":
    main()
