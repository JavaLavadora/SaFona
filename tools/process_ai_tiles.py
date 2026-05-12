"""Process AI-generated tile images into auto-tile strips for Sa Fona.

Takes a single AI-generated image with 4 tiles on green background
(top_grass, inner_stone, underground, wall_edge) and produces an
auto-tile strip ({NUM_TILES}*{TILE_SIZE} x {TILE_SIZE} px) with 16
bitmask variants.

Usage:
    conda activate safona
    python tools/process_ai_tiles.py [input_image] [output_path]

Defaults:
    input:  assets/exmaple_tiles.png
    output: assets/tilesets/world1/tileset.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TILE_SIZE = 24
NUM_TILES = 16

UP = 1
DOWN = 2
LEFT = 4
RIGHT = 8


def extract_tiles(image_path: Path) -> list[np.ndarray]:
    """Extract tile regions from an AI image with green background."""
    arr = np.array(Image.open(image_path))
    if arr.shape[2] == 4:
        arr = arr[:, :, :3]

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    gi, ri, bi = g.astype(int), r.astype(int), b.astype(int)
    is_green = (gi - ri > 40) & (gi - bi > 40) & (g > 80)

    labeled, _ = ndimage.label(~is_green)
    tiles: list[np.ndarray] = []

    for region_id in range(1, labeled.max() + 1):
        ys, xs = np.where(labeled == region_id)
        if len(ys) < 1000:
            continue
        y0, y1 = ys.min(), ys.max()
        x0, x1 = xs.min(), xs.max()

        inset = 5
        crop = arr[y0 + inset : y1 - inset + 1, x0 + inset : x1 - inset + 1].copy()

        cr, cg, cb = (
            crop[:, :, 0].astype(int),
            crop[:, :, 1].astype(int),
            crop[:, :, 2].astype(int),
        )
        green_mask = (cg - cr > 30) & (cg - cb > 30) & (cg > 100)
        if green_mask.any():
            for cy in range(crop.shape[0]):
                for cx in range(crop.shape[1]):
                    if green_mask[cy, cx]:
                        neighbors = []
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                ny, nx = cy + dy, cx + dx
                                if 0 <= ny < crop.shape[0] and 0 <= nx < crop.shape[1]:
                                    if not green_mask[ny, nx]:
                                        neighbors.append(crop[ny, nx])
                        if neighbors:
                            crop[cy, cx] = np.mean(neighbors, axis=0).astype(np.uint8)

        tiles.append(crop)

    if len(tiles) != 4:
        print(f"Warning: expected 4 tiles, found {len(tiles)}")
    return tiles


def downscale_tile(tile_arr: np.ndarray, target: int = TILE_SIZE) -> Image.Image:
    """Single high-quality LANCZOS downscale to target size."""
    pil = Image.fromarray(tile_arr)
    return pil.resize((target, target), Image.LANCZOS)


def build_autotile_strip(
    top_grass: Image.Image,
    inner_stone: Image.Image,
    underground: Image.Image,
    wall_edge: Image.Image,
) -> Image.Image:
    """Build an auto-tile strip from 4 base tiles."""
    strip = Image.new("RGBA", (NUM_TILES * TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    edge_w = max(1, TILE_SIZE // 12)

    bases = {
        "top_grass": top_grass.convert("RGBA"),
        "inner_stone": inner_stone.convert("RGBA"),
        "underground": underground.convert("RGBA"),
        "wall_edge": wall_edge.convert("RGBA"),
    }

    for mask in range(1, NUM_TILES):
        has_up = bool(mask & UP)
        has_down = bool(mask & DOWN)
        has_left = bool(mask & LEFT)
        has_right = bool(mask & RIGHT)

        if mask == 15:
            base = bases["underground"].copy()
        elif not has_up:
            base = bases["top_grass"].copy()
        elif has_up and not has_down:
            base = bases["wall_edge"].copy()
        else:
            base = bases["inner_stone"].copy()

        px = base.load()
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                r, g, b, a = px[x, y]
                darken = False
                if not has_left and x < edge_w:
                    darken = True
                if not has_right and x >= TILE_SIZE - edge_w:
                    darken = True
                if not has_down and y >= TILE_SIZE - edge_w:
                    darken = True
                if darken:
                    f = 0.75
                    px[x, y] = (int(r * f), int(g * f), int(b * f), a)

        strip.paste(base, (mask * TILE_SIZE, 0))

    return strip


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "assets" / "exmaple_tiles.png"
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else PROJECT_ROOT / "assets" / "tilesets" / "world1" / "tileset.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")

    tiles = extract_tiles(input_path)
    if len(tiles) < 4:
        print(f"Error: need 4 tiles, found {len(tiles)}")
        sys.exit(1)

    processed = [
        tiles[0],                                                       # top_grass (raw)
        tiles[1],                                                       # inner_stone (raw)
        np.clip(tiles[2].astype(np.float32) * 0.7, 0, 255).astype(np.uint8),  # underground (darkened)
        tiles[3],                                                       # wall_edge (raw)
    ]

    small = [downscale_tile(t) for t in processed]
    strip = build_autotile_strip(*small)
    strip.save(str(output_path))
    print(f"Saved: {output_path} ({strip.size[0]}x{strip.size[1]})")


if __name__ == "__main__":
    main()
