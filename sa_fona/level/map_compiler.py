"""Auto-compile .map + .yaml level sources into .json on game startup.

Scans the levels directory for .map files and converts any that are
newer than their corresponding .json. This makes .map + .yaml the
source of truth while keeping the engine's JSON loader working as-is.

Usage from the game entry point::

    from sa_fona.level.map_compiler import compile_all_maps
    compile_all_maps()  # call before any level loading
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# The tools/ directory lives at the project root, two levels up from this file.
_TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools"


def _ensure_tools_importable() -> None:
    """Add the tools/ directory to sys.path if not already present."""
    tools_str = str(_TOOLS_DIR)
    if tools_str not in sys.path:
        sys.path.insert(0, tools_str)


def compile_map_file(map_path: Path) -> bool:
    """Compile a single .map + .yaml pair into .json.

    Args:
        map_path: Path to the .map file. A matching .yaml file must
            exist in the same directory with the same stem.

    Returns:
        True if the .json was (re)written, False if skipped.

    Raises:
        FileNotFoundError: If the matching .yaml file is missing.
    """
    _ensure_tools_importable()
    from map_to_json import (
        build_level_json,
        load_yaml_metadata,
        parse_map_file,
    )

    yaml_path = map_path.with_suffix(".yaml")
    json_path = map_path.with_suffix(".json")

    if not yaml_path.exists():
        logger.warning("Skipping %s: no matching .yaml file", map_path)
        return False

    # Check modification times: skip if .json is up to date
    if json_path.exists():
        json_mtime = json_path.stat().st_mtime
        map_mtime = map_path.stat().st_mtime
        yaml_mtime = yaml_path.stat().st_mtime
        if json_mtime >= map_mtime and json_mtime >= yaml_mtime:
            return False

    # Convert
    grid, spawns = parse_map_file(str(map_path))
    yaml_data = load_yaml_metadata(str(yaml_path))
    level_json = build_level_json(grid, spawns, yaml_data)

    json_str = json.dumps(level_json, indent=2)
    json_path.write_text(json_str + "\n", encoding="utf-8")

    logger.info("Compiled %s -> %s", map_path.name, json_path.name)
    return True


def compile_all_maps(levels_dir: Path | None = None) -> int:
    """Scan for .map files and compile any that need updating.

    Args:
        levels_dir: Root levels directory. Defaults to the standard
            ``sa_fona/data/levels/`` location.

    Returns:
        Number of levels that were (re)compiled.
    """
    if levels_dir is None:
        from sa_fona.config.settings import DATA_DIR
        levels_dir = DATA_DIR / "levels"

    if not levels_dir.exists():
        logger.debug("Levels directory does not exist: %s", levels_dir)
        return 0

    compiled = 0
    map_files = sorted(levels_dir.rglob("*.map"))

    if not map_files:
        logger.debug("No .map files found in %s", levels_dir)
        return 0

    for map_path in map_files:
        try:
            if compile_map_file(map_path):
                compiled += 1
        except Exception:
            logger.exception("Failed to compile %s", map_path)

    if compiled:
        logger.info("Map compiler: %d level(s) compiled", compiled)
    else:
        logger.debug("Map compiler: all levels up to date")

    return compiled
