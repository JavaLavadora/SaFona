"""Sprite sheet generator for Sa Fona.

Reads sprite definitions from tools/sprite_defs/, converts text grids
to PIL Images, assembles horizontal sprite sheets, and writes PNGs
to the assets/ directory.

Usage:
    conda activate safona
    python tools/generate_sprites.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_MANIFEST = PROJECT_ROOT / "sa_fona" / "data" / "asset_manifest.json"
ASSETS_DIR = PROJECT_ROOT / "assets"

sys.path.insert(0, str(PROJECT_ROOT))


def load_manifest() -> dict[str, Any]:
    """Load and return the sprites section of asset_manifest.json."""
    with open(ASSET_MANIFEST) as f:
        return json.load(f)["sprites"]


def parse_grid(grid: str, width: int, height: int) -> str:
    """Parse a multiline grid string into a flat pixel string.

    Strips leading/trailing whitespace, splits into rows, and pads
    each row with '.' to the expected width. This makes sprite
    definitions forgiving about trailing dots.

    Args:
        grid: Multiline or flat grid string.
        width: Expected row width.
        height: Expected number of rows.

    Returns:
        A flat string of exactly width * height characters.

    Raises:
        ValueError: If row count or any row width is wrong.
    """
    lines = [line for line in grid.strip().splitlines() if line.strip()]
    if not lines:
        return "." * (width * height)

    if len(lines) != height:
        raise ValueError(
            f"Grid has {len(lines)} rows, expected {height}"
        )

    flat = []
    for i, line in enumerate(lines):
        row = line.strip()
        if len(row) > width:
            raise ValueError(
                f"Row {i} has {len(row)} chars (max {width}): \"{row}\""
            )
        flat.append(row.ljust(width, "."))

    return "".join(flat)


def grid_to_frame(
    grid: str,
    palette: dict[str, tuple[int, int, int, int]],
    width: int,
    height: int,
) -> Image.Image:
    """Convert a grid string + palette into a PIL RGBA Image.

    Accepts both flat strings and multiline strings (parsed via
    parse_grid).

    Args:
        grid: Grid string (multiline or flat).
        palette: Mapping of single characters to RGBA tuples.
        width: Frame width in pixels.
        height: Frame height in pixels.

    Returns:
        A PIL Image in RGBA mode.
    """
    flat = parse_grid(grid, width, height)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = img.load()
    for i, char in enumerate(flat):
        x = i % width
        y = i // width
        if char in palette:
            pixels[x, y] = palette[char]
    return img


def frames_to_sheet(frames: list[Image.Image], width: int, height: int) -> Image.Image:
    """Combine frames into a horizontal sprite sheet.

    Args:
        frames: List of PIL Images, each width x height.
        width: Width of a single frame.
        height: Height of a single frame.

    Returns:
        A PIL Image of size (width * len(frames), height).
    """
    sheet = Image.new("RGBA", (width * len(frames), height), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * width, 0))
    return sheet


def generate_sprite_sheet(
    sprite_module: Any,
    animation_name: str,
    output_path: Path,
    expected_width: int | None = None,
    expected_height: int | None = None,
    expected_frames: int | None = None,
) -> None:
    """Generate a single sprite sheet PNG from a sprite definition module.

    Args:
        sprite_module: Module with PALETTE, WIDTH, HEIGHT, and ANIMATIONS dict.
        animation_name: Key in the module's ANIMATIONS dict.
        output_path: Where to write the PNG.
        expected_width: If set, validate frame width matches.
        expected_height: If set, validate frame height matches.
        expected_frames: If set, validate frame count matches.
    """
    palette = sprite_module.PALETTE
    width = sprite_module.WIDTH
    height = sprite_module.HEIGHT
    grids = sprite_module.ANIMATIONS[animation_name]

    if expected_width and width != expected_width:
        raise ValueError(
            f"Width mismatch: definition says {width}, "
            f"manifest says {expected_width}"
        )
    if expected_height and height != expected_height:
        raise ValueError(
            f"Height mismatch: definition says {height}, "
            f"manifest says {expected_height}"
        )
    if expected_frames and len(grids) != expected_frames:
        raise ValueError(
            f"Frame count mismatch: definition has {len(grids)}, "
            f"manifest says {expected_frames}"
        )

    frames = [grid_to_frame(g, palette, width, height) for g in grids]

    if getattr(sprite_module, "MIRROR", False):
        frames = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]

    sheet = frames_to_sheet(frames, width, height)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output_path))
    print(f"  {output_path.relative_to(PROJECT_ROOT)} ({width*len(frames)}x{height}, {len(frames)} frames)")


def generate_custom_sprite(
    palette: dict[str, tuple[int, int, int, int]],
    grids: list[str],
    width: int,
    height: int,
    output_path: Path,
    label: str,
) -> None:
    """Generate a sprite sheet from raw palette/grids (no module wrapper)."""
    frames = [grid_to_frame(g, palette, width, height) for g in grids]
    sheet = frames_to_sheet(frames, width, height)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output_path))
    print(f"  {output_path.relative_to(PROJECT_ROOT)} ({width*len(frames)}x{height}, {len(frames)} frames)")


SPRITE_REGISTRY: list[dict[str, str]] = [
    # Player
    {"module": "tools.sprite_defs.balchar", "animation": "idle", "manifest_key": "balchar_idle"},
    {"module": "tools.sprite_defs.balchar", "animation": "walk", "manifest_key": "balchar_walk"},
    {"module": "tools.sprite_defs.balchar", "animation": "jump", "manifest_key": "balchar_jump"},
    {"module": "tools.sprite_defs.balchar", "animation": "wall_slide", "manifest_key": "balchar_wall_slide"},
    {"module": "tools.sprite_defs.balchar", "animation": "wall_jump", "manifest_key": "balchar_wall_jump"},
    # Companion
    {"module": "tools.sprite_defs.bep", "animation": "idle", "manifest_key": "bep_idle"},
    # Enemies
    {"module": "tools.sprite_defs.possessed_sheep", "animation": "idle", "manifest_key": "enemy_possessed_sheep_idle"},
    {"module": "tools.sprite_defs.possessed_sheep", "animation": "walk", "manifest_key": "enemy_possessed_sheep_walk"},
    {"module": "tools.sprite_defs.rival_warrior", "animation": "idle", "manifest_key": "enemy_rival_warrior_idle"},
    {"module": "tools.sprite_defs.rival_warrior", "animation": "walk", "manifest_key": "enemy_rival_warrior_walk"},
    {"module": "tools.sprite_defs.stone_guardian", "animation": "idle", "manifest_key": "enemy_stone_guardian_idle"},
    {"module": "tools.sprite_defs.stone_guardian", "animation": "walk", "manifest_key": "enemy_stone_guardian_walk"},
]

CUSTOM_SPRITES: list[dict] = [
    {
        "module": "tools.sprite_defs.pickups",
        "palette_attr": "HEART_PALETTE_MAP",
        "grids_attr": "HEART",
        "width_attr": "HEART_W",
        "height_attr": "HEART_H",
        "manifest_key": "pickup_heart",
    },
    {
        "module": "tools.sprite_defs.pickups",
        "palette_attr": "STONE_PALETTE_MAP",
        "grids_attr": "STONE",
        "width_attr": "STONE_W",
        "height_attr": "STONE_H",
        "manifest_key": "pickup_stone",
    },
    {
        "module": "tools.sprite_defs.breakables",
        "palette_attr": "POT_PALETTE_MAP",
        "grids_attr": "POT",
        "width_attr": "POT_W",
        "height_attr": "POT_H",
        "manifest_key": "breakable_pot",
    },
    {
        "module": "tools.sprite_defs.breakables",
        "palette_attr": "CRATE_PALETTE_MAP",
        "grids_attr": "CRATE",
        "width_attr": "CRATE_W",
        "height_attr": "CRATE_H",
        "manifest_key": "breakable_crate",
    },
]


def main() -> None:
    """Generate all registered sprite sheets."""
    import importlib

    manifest = load_manifest()

    print("Generating sprite sheets...")
    generated = 0
    errors = 0

    for entry in SPRITE_REGISTRY:
        mod = importlib.import_module(entry["module"])
        manifest_key = entry["manifest_key"]
        manifest_entry = manifest.get(manifest_key, {})

        output_path = ASSETS_DIR / Path(manifest_entry.get(
            "path", f"sprites/{manifest_key}.png"
        )).relative_to("assets") if "path" in manifest_entry else ASSETS_DIR / "sprites" / f"{manifest_key}.png"

        try:
            generate_sprite_sheet(
                mod,
                entry["animation"],
                output_path,
                expected_width=manifest_entry.get("frame_width"),
                expected_height=manifest_entry.get("frame_height"),
                expected_frames=manifest_entry.get("frame_count"),
            )
            generated += 1
        except (ValueError, KeyError) as exc:
            print(f"  ERROR ({manifest_key}): {exc}")
            errors += 1

    for entry in CUSTOM_SPRITES:
        mod = importlib.import_module(entry["module"])
        manifest_key = entry["manifest_key"]
        manifest_entry = manifest.get(manifest_key, {})

        palette = getattr(mod, entry["palette_attr"])
        grids = getattr(mod, entry["grids_attr"])
        width = getattr(mod, entry["width_attr"])
        height = getattr(mod, entry["height_attr"])

        output_path = (
            ASSETS_DIR / Path(manifest_entry["path"]).relative_to("assets")
            if "path" in manifest_entry
            else ASSETS_DIR / "sprites" / f"{manifest_key}.png"
        )

        try:
            generate_custom_sprite(palette, grids, width, height, output_path, manifest_key)
            generated += 1
        except (ValueError, KeyError) as exc:
            print(f"  ERROR ({manifest_key}): {exc}")
            errors += 1

    print(f"\nDone: {generated} generated, {errors} errors.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
