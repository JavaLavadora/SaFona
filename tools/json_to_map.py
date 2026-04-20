#!/usr/bin/env python3
"""Convert a level JSON file back to .map + .yaml format.

This is a utility for converting existing JSON level files into the
human-readable ASCII .map + .yaml pair used by the level editor.

Usage:
    python tools/json_to_map.py sa_fona/data/levels/world1/level_1_1.json
    python tools/json_to_map.py sa_fona/data/levels/world1/level_1_1.json -o /tmp/out
    python tools/json_to_map.py --all   # Convert all levels in sa_fona/data/levels/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


# Tile ID -> ASCII character (standard mapping from map_to_json.py)
TILE_TO_CHAR: dict[int, str] = {
    0: ".",
    1: "#",
    10: "-",
    20: "X",
    30: "B",
}


def json_to_map_and_yaml(
    json_data: dict[str, Any],
) -> tuple[str, str]:
    """Convert a level JSON dict to .map text and .yaml text.

    Args:
        json_data: Parsed level JSON dict.

    Returns:
        Tuple of (map_text, yaml_text).
    """
    metadata = json_data["metadata"]
    dimensions = json_data["dimensions"]
    midground = json_data["layers"]["midground"]
    player_spawn = json_data["player_spawn"]
    companion_spawn = json_data["companion_spawn"]
    entities = json_data.get("entities", [])
    triggers = json_data.get("triggers", [])
    secrets = json_data.get("secrets", [])
    parallax = json_data.get("parallax", {})

    width = dimensions["width"]
    height = dimensions["height"]

    # Build the ASCII grid
    name = metadata.get("name", "Unknown")
    name_en = metadata.get("name_en", "Unknown")
    w = metadata.get("world", 0)
    lv = metadata.get("level", 0)

    lines: list[str] = []
    lines.append(f"// Level {w}-{lv}: {name} ({name_en})")
    lines.append(f"// {width} x {height} tiles")
    lines.append(
        "// Legend: . = air, # = solid, - = one-way, "
        "X = hazard, B = breakable, P = player, C = companion"
    )

    px, py = player_spawn["x"], player_spawn["y"]
    cx, cy = companion_spawn["x"], companion_spawn["y"]

    for row_idx, row in enumerate(midground):
        row_chars: list[str] = []
        for col_idx, tile_id in enumerate(row):
            if col_idx == px and row_idx == py:
                row_chars.append("P")
            elif col_idx == cx and row_idx == cy:
                row_chars.append("C")
            else:
                ch = TILE_TO_CHAR.get(tile_id)
                if ch is None:
                    # Unknown tile ID -- use '?' but warn
                    print(
                        f"WARNING: Unknown tile ID {tile_id} at ({col_idx}, {row_idx}), "
                        "using '?' placeholder",
                        file=sys.stderr,
                    )
                    ch = "."  # Fall back to air for safety
                row_chars.append(ch)
        lines.append("".join(row_chars))

    map_text = "\n".join(lines) + "\n"

    # Build YAML structure
    yaml_data: dict[str, Any] = {}

    # metadata section
    yaml_data["metadata"] = {
        "world": metadata["world"],
        "level": metadata["level"],
        "name": metadata["name"],
        "name_en": metadata["name_en"],
        "music_slot": metadata["music_slot"],
        "difficulty": metadata["difficulty"],
        "tileset": metadata["tileset"],
        "background": metadata["background"],
    }

    # Split entities into enemies, pickups, breakables
    enemies: list[dict[str, Any]] = []
    pickups: list[dict[str, Any]] = []
    breakables: list[dict[str, Any]] = []

    for entity in entities:
        etype = entity["type"]
        if etype == "enemy":
            enemies.append({
                "type": entity["enemy_type"],
                "x": entity["x"],
                "y": entity["y"],
            })
        elif etype == "pickup":
            pickup: dict[str, Any] = {
                "type": entity["pickup_type"],
                "x": entity["x"],
                "y": entity["y"],
            }
            if "value" in entity:
                pickup["value"] = entity["value"]
            pickups.append(pickup)
        elif etype == "breakable":
            breakables.append({
                "type": entity["breakable_type"],
                "x": entity["x"],
                "y": entity["y"],
            })

    yaml_data["enemies"] = enemies
    yaml_data["pickups"] = pickups
    yaml_data["breakables"] = breakables
    yaml_data["triggers"] = triggers if triggers else []
    yaml_data["secrets"] = secrets if secrets else []
    yaml_data["parallax"] = parallax if parallax else {}

    yaml_text = yaml.dump(
        yaml_data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )

    return map_text, yaml_text


def convert_json_file(json_path: str, output_dir: str | None = None) -> tuple[str, str]:
    """Convert a single JSON level file to .map + .yaml.

    Args:
        json_path: Path to the JSON level file.
        output_dir: Directory for output files. If None, uses same directory as JSON.

    Returns:
        Tuple of (map_output_path, yaml_output_path).
    """
    json_p = Path(json_path)
    with open(json_p, encoding="utf-8") as f:
        data = json.load(f)

    map_text, yaml_text = json_to_map_and_yaml(data)

    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = json_p.parent

    out_dir.mkdir(parents=True, exist_ok=True)

    stem = json_p.stem
    map_path = out_dir / f"{stem}.map"
    yaml_path = out_dir / f"{stem}.yaml"

    map_path.write_text(map_text, encoding="utf-8")
    yaml_path.write_text(yaml_text, encoding="utf-8")

    return str(map_path), str(yaml_path)


def convert_all_levels(levels_dir: str) -> list[tuple[str, str]]:
    """Convert all JSON level files under a directory.

    Args:
        levels_dir: Root directory containing level JSON files.

    Returns:
        List of (map_path, yaml_path) tuples for each converted level.
    """
    results = []
    levels_path = Path(levels_dir)

    for json_file in sorted(levels_path.rglob("*.json")):
        print(f"Converting {json_file}...", file=sys.stderr)
        map_path, yaml_path = convert_json_file(str(json_file))
        results.append((map_path, yaml_path))
        print(f"  -> {map_path}", file=sys.stderr)
        print(f"  -> {yaml_path}", file=sys.stderr)

    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(
        description="Convert level JSON files to .map + .yaml format.",
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        help="Path to a JSON level file to convert",
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as input)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Convert all levels in sa_fona/data/levels/",
    )

    args = parser.parse_args(argv)

    if args.all:
        base = Path(__file__).resolve().parent.parent
        levels_dir = base / "sa_fona" / "data" / "levels"
        results = convert_all_levels(str(levels_dir))
        print(f"\nConverted {len(results)} level(s).", file=sys.stderr)
        return 0

    if not args.json_file:
        parser.error("Provide a JSON file path or use --all")

    try:
        map_path, yaml_path = convert_json_file(args.json_file, args.output_dir)
        print(f"Map:  {map_path}", file=sys.stderr)
        print(f"YAML: {yaml_path}", file=sys.stderr)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
