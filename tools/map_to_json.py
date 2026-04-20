#!/usr/bin/env python3
"""Convert ASCII tilemap + YAML metadata into the engine's JSON level format.

This is a standalone build tool for Sa Fona level creation. It reads a
human-readable ``.map`` file (ASCII grid) and a ``.yaml`` metadata file,
then outputs a JSON level file structurally identical to what the game
engine expects.

Usage:
    python tools/map_to_json.py input.map input.yaml -o output.json
    python tools/map_to_json.py input.map input.yaml  # stdout
    python tools/map_to_json.py input.map input.yaml --preview
    python tools/map_to_json.py input.map input.yaml --validate-only
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import yaml


# ── ASCII character → tile ID mapping ─────────────────────────────────

CHAR_TO_TILE: dict[str, int] = {
    ".": 0,   # air
    "#": 1,   # solid
    "-": 10,  # one-way platform
    "X": 20,  # hazard
    "B": 30,  # breakable_slam
}

# Special markers (record position, tile becomes 0)
SPAWN_CHARS: set[str] = {"P", "C"}

# Reverse mapping for preview display
TILE_TO_CHAR: dict[int, str] = {v: k for k, v in CHAR_TO_TILE.items() if v != 0}
TILE_TO_CHAR[0] = "."

# Collision type registry: tile_id → category name
COLLISION_CATEGORIES: dict[int, str] = {
    1: "solid",
    10: "one_way",
    20: "hazard",
    30: "breakable_slam",
}

# Required metadata fields
REQUIRED_METADATA_FIELDS: list[str] = [
    "world", "level", "name", "name_en", "music_slot",
    "difficulty", "tileset", "background",
]


class MapParseError(Exception):
    """Raised when the .map file has structural errors."""


class YamlParseError(Exception):
    """Raised when the .yaml file has structural errors."""


# ── Grid parsing ──────────────────────────────────────────────────────


def parse_map_file(map_path: str) -> tuple[list[list[int]], dict[str, tuple[int, int]]]:
    """Parse an ASCII .map file into a 2D tile grid and spawn positions.

    Args:
        map_path: Path to the .map file.

    Returns:
        A tuple of (grid, spawns) where grid is a 2D list of tile IDs
        and spawns is a dict mapping 'P' and/or 'C' to (x, y) positions.

    Raises:
        MapParseError: If the file has invalid characters, inconsistent
            row widths, or is missing a player spawn.
    """
    path = Path(map_path)
    raw_text = path.read_text(encoding="utf-8")
    return parse_map_string(raw_text, source=str(path))


def parse_map_string(text: str, source: str = "<string>") -> tuple[list[list[int]], dict[str, tuple[int, int]]]:
    """Parse an ASCII map string into a 2D tile grid and spawn positions.

    Args:
        text: The map text content.
        source: Source identifier for error messages.

    Returns:
        A tuple of (grid, spawns).

    Raises:
        MapParseError: On invalid content.
    """
    lines = text.splitlines()

    # Filter out comment lines (starting with //) and strip trailing whitespace.
    # Keep track of original line numbers for error reporting.
    data_rows: list[tuple[int, str]] = []
    for line_num, line in enumerate(lines, start=1):
        stripped = line.rstrip()
        if stripped.startswith("//"):
            continue
        if stripped == "" and not data_rows:
            # Skip leading empty lines
            continue
        if stripped == "":
            # Skip trailing empty lines — but if we have data rows already,
            # we'll handle this after we find the last non-empty row.
            data_rows.append((line_num, stripped))
            continue
        data_rows.append((line_num, stripped))

    # Remove trailing empty rows
    while data_rows and data_rows[-1][1] == "":
        data_rows.pop()

    if not data_rows:
        raise MapParseError(f"{source}: Map file is empty (no data rows found).")

    # Check for empty lines in the middle (they would break the grid)
    for line_num, row_text in data_rows:
        if row_text == "":
            raise MapParseError(
                f"{source}:{line_num}: Empty line in the middle of the map grid."
            )

    # Validate consistent width
    widths = [(line_num, len(row_text)) for line_num, row_text in data_rows]
    expected_width = widths[0][1]
    for line_num, w in widths:
        if w != expected_width:
            raise MapParseError(
                f"{source}:{line_num}: Row width {w} differs from first row width "
                f"{expected_width} (line {widths[0][0]})."
            )

    # Parse characters into tile IDs and detect spawns
    grid: list[list[int]] = []
    spawns: dict[str, tuple[int, int]] = {}
    valid_chars = set(CHAR_TO_TILE.keys()) | SPAWN_CHARS

    for row_idx, (line_num, row_text) in enumerate(data_rows):
        row: list[int] = []
        for col_idx, ch in enumerate(row_text):
            if ch not in valid_chars:
                raise MapParseError(
                    f"{source}:{line_num}:{col_idx + 1}: Unknown character '{ch}'."
                )

            if ch in SPAWN_CHARS:
                if ch in spawns:
                    raise MapParseError(
                        f"{source}:{line_num}:{col_idx + 1}: Duplicate '{ch}' marker. "
                        f"First at ({spawns[ch][0]}, {spawns[ch][1]})."
                    )
                spawns[ch] = (col_idx, row_idx)
                row.append(0)  # Spawn positions are air tiles
            else:
                row.append(CHAR_TO_TILE[ch])
        grid.append(row)

    # Validate spawns
    if "P" not in spawns:
        raise MapParseError(
            f"{source}: Missing 'P' (player spawn) marker in map."
        )

    if "C" not in spawns:
        # Default companion spawn: 1 tile left of player
        px, py = spawns["P"]
        cx = max(0, px - 1)
        spawns["C"] = (cx, py)
        warnings.warn(
            f"{source}: No 'C' (companion spawn) marker; defaulting to "
            f"({cx}, {py}), 1 tile left of player.",
            stacklevel=2,
        )

    return grid, spawns


# ── YAML loading ──────────────────────────────────────────────────────


def load_yaml_metadata(yaml_path: str) -> dict[str, Any]:
    """Load and validate a YAML metadata file.

    Args:
        yaml_path: Path to the .yaml file.

    Returns:
        Parsed YAML dict.

    Raises:
        YamlParseError: If required fields are missing or YAML is invalid.
    """
    path = Path(yaml_path)
    try:
        raw_text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise YamlParseError(f"YAML parse error in {yaml_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise YamlParseError(
            f"{yaml_path}: Expected a YAML mapping at top level, got {type(data).__name__}."
        )

    # Validate required metadata fields
    metadata = data.get("metadata")
    if metadata is None:
        raise YamlParseError(f"{yaml_path}: Missing 'metadata' section.")

    missing = [f for f in REQUIRED_METADATA_FIELDS if f not in metadata]
    if missing:
        raise YamlParseError(
            f"{yaml_path}: Missing required metadata fields: {', '.join(missing)}"
        )

    return data


# ── Collision type detection ──────────────────────────────────────────


def detect_collision_types(grid: list[list[int]]) -> dict[str, list[int]]:
    """Build the collision_types mapping for the level.

    Always includes all standard collision categories (solid, one_way,
    hazard, breakable_slam) to match the engine's expected format,
    regardless of whether those tile types appear in the grid.

    Args:
        grid: 2D list of tile IDs.

    Returns:
        Dict mapping category name to list of tile IDs.
    """
    # Group tile IDs by category in a fixed order
    category_order = ["solid", "one_way", "hazard", "breakable_slam"]
    category_tiles: dict[str, list[int]] = {cat: [] for cat in category_order}

    for tid, category in sorted(COLLISION_CATEGORIES.items(), key=lambda x: x[0]):
        category_tiles[category].append(tid)

    return category_tiles


# ── Entity building ───────────────────────────────────────────────────


def build_entities(yaml_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the entities list from YAML enemy, pickup, and breakable sections.

    Args:
        yaml_data: Parsed YAML dict.

    Returns:
        List of entity dicts matching the engine JSON format.
    """
    entities: list[dict[str, Any]] = []

    # Pickups
    for pickup in yaml_data.get("pickups", []):
        entity: dict[str, Any] = {
            "type": "pickup",
            "pickup_type": pickup["type"],
            "x": pickup["x"],
            "y": pickup["y"],
        }
        if "value" in pickup:
            entity["value"] = pickup["value"]
        entities.append(entity)

    # Breakables
    for breakable in yaml_data.get("breakables", []):
        entity = {
            "type": "breakable",
            "breakable_type": breakable["type"],
            "x": breakable["x"],
            "y": breakable["y"],
        }
        entities.append(entity)

    # Enemies
    for enemy in yaml_data.get("enemies", []):
        entity = {
            "type": "enemy",
            "enemy_type": enemy["type"],
            "x": enemy["x"],
            "y": enemy["y"],
        }
        entities.append(entity)

    return entities


# ── JSON assembly ─────────────────────────────────────────────────────


def make_empty_layer(width: int, height: int) -> list[list[int]]:
    """Create a 2D grid of zeros with the given dimensions.

    Args:
        width: Number of columns.
        height: Number of rows.

    Returns:
        2D list of zeros.
    """
    return [[0] * width for _ in range(height)]


def build_level_json(
    grid: list[list[int]],
    spawns: dict[str, tuple[int, int]],
    yaml_data: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the complete level JSON structure.

    Args:
        grid: 2D tile ID grid (midground layer).
        spawns: Dict with 'P' and 'C' spawn positions.
        yaml_data: Parsed YAML metadata.

    Returns:
        Complete level dict ready for JSON serialization.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    metadata = yaml_data.get("metadata", {})
    collision_types = detect_collision_types(grid)
    entities = build_entities(yaml_data)
    triggers = yaml_data.get("triggers", [])
    secrets = yaml_data.get("secrets", [])
    parallax = yaml_data.get("parallax", {})

    # If parallax is None, default to empty
    if parallax is None:
        parallax = {}

    level: dict[str, Any] = {
        "metadata": {
            "world": metadata["world"],
            "level": metadata["level"],
            "name": metadata["name"],
            "name_en": metadata["name_en"],
            "music_slot": metadata["music_slot"],
            "difficulty": metadata["difficulty"],
            "tileset": metadata["tileset"],
            "background": metadata["background"],
        },
        "dimensions": {
            "width": width,
            "height": height,
        },
        "collision_types": collision_types,
        "layers": {
            "background": make_empty_layer(width, height),
            "midground": grid,
            "foreground": make_empty_layer(width, height),
        },
        "player_spawn": {
            "x": spawns["P"][0],
            "y": spawns["P"][1],
        },
        "companion_spawn": {
            "x": spawns["C"][0],
            "y": spawns["C"][1],
        },
        "entities": entities,
        "triggers": triggers,
        "secrets": secrets,
        "parallax": parallax,
    }

    return level


# ── Preview ───────────────────────────────────────────────────────────


def preview_map(
    grid: list[list[int]],
    spawns: dict[str, tuple[int, int]],
    yaml_data: dict[str, Any],
) -> str:
    """Generate a human-readable preview of the parsed map.

    Args:
        grid: 2D tile ID grid.
        spawns: Spawn positions.
        yaml_data: Parsed YAML data.

    Returns:
        Multi-line string with the ASCII map and summary.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("MAP PREVIEW")
    lines.append("=" * 60)

    # Render the grid back to ASCII
    for row_idx, row in enumerate(grid):
        row_chars: list[str] = []
        for col_idx, tid in enumerate(row):
            pos = (col_idx, row_idx)
            if pos == spawns.get("P"):
                row_chars.append("P")
            elif pos == spawns.get("C"):
                row_chars.append("C")
            else:
                row_chars.append(TILE_TO_CHAR.get(tid, "?"))
        lines.append("".join(row_chars))

    lines.append("")
    lines.append("-" * 60)
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"  Dimensions:      {width} x {height} tiles")
    lines.append(f"  Player spawn:    ({spawns['P'][0]}, {spawns['P'][1]})")
    lines.append(f"  Companion spawn: ({spawns['C'][0]}, {spawns['C'][1]})")

    metadata = yaml_data.get("metadata", {})
    lines.append(f"  Level name:      {metadata.get('name', 'N/A')}")

    enemies = yaml_data.get("enemies", [])
    pickups = yaml_data.get("pickups", [])
    breakables = yaml_data.get("breakables", [])
    triggers = yaml_data.get("triggers", [])
    secrets = yaml_data.get("secrets", [])

    lines.append(f"  Enemies:         {len(enemies)}")
    lines.append(f"  Pickups:         {len(pickups)}")
    lines.append(f"  Breakables:      {len(breakables)}")
    lines.append(f"  Triggers:        {len(triggers)}")
    lines.append(f"  Secrets:         {len(secrets)}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the ASCII level editor tool.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    parser = argparse.ArgumentParser(
        description="Convert ASCII tilemap + YAML metadata into engine JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Character mapping:\n"
            "  .  = air (tile 0)\n"
            "  #  = solid (tile 1)\n"
            "  -  = one-way platform (tile 10)\n"
            "  X  = hazard (tile 20)\n"
            "  B  = breakable (tile 30)\n"
            "  P  = player spawn\n"
            "  C  = companion spawn"
        ),
    )
    parser.add_argument("map_file", help="Path to the .map ASCII tilemap file")
    parser.add_argument("yaml_file", help="Path to the .yaml metadata file")
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print an ASCII map preview with summary instead of JSON",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Parse and validate without producing output",
    )

    args = parser.parse_args(argv)

    try:
        grid, spawns = parse_map_file(args.map_file)
        yaml_data = load_yaml_metadata(args.yaml_file)
    except (MapParseError, YamlParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.validate_only:
        height = len(grid)
        width = len(grid[0]) if height else 0
        print(f"Validation passed: {width}x{height} grid, "
              f"player at ({spawns['P'][0]}, {spawns['P'][1]})")
        return 0

    if args.preview:
        print(preview_map(grid, spawns, yaml_data))
        return 0

    # Build and output JSON
    level_json = build_level_json(grid, spawns, yaml_data)
    json_str = json.dumps(level_json, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_str + "\n", encoding="utf-8")
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        print(json_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
