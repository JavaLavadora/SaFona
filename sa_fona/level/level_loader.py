"""Load a level from its JSON data file and produce runtime data."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sa_fona.level.tilemap import TileMap


@dataclass
class LevelData:
    """Container for all runtime data produced by loading a level.

    Attributes:
        tilemap: The tile-based level geometry.
        entities: Raw entity dicts (no Entity class yet).
        triggers: Raw trigger dicts.
        parallax_layers: Parallax background layer definitions.
        metadata: Level metadata (world, name, music, etc.).
        player_spawn: ``(tile_x, tile_y)`` grid coordinates for the player.
        companion_spawn: ``(tile_x, tile_y)`` grid coordinates for the companion.
    """

    tilemap: TileMap
    entities: list[dict] = field(default_factory=list)
    triggers: list[dict] = field(default_factory=list)
    parallax_layers: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    player_spawn: tuple[int, int] = (0, 0)
    companion_spawn: tuple[int, int] = (0, 0)


class LevelLoader:
    """Loads a level from its JSON data file.

    For D2 this is a simplified loader: it reads the JSON, builds a
    TileMap with placeholder rendering, and extracts entity/trigger
    lists without further processing.
    """

    def load(self, level_path: str) -> LevelData:
        """Load and parse a level JSON file.

        Args:
            level_path: Filesystem path to the level ``.json`` file.

        Returns:
            A populated ``LevelData`` instance.

        Raises:
            FileNotFoundError: If the level file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If required fields are missing from the JSON.
        """
        with open(level_path, "r", encoding="utf-8") as fh:
            data: dict = json.load(fh)

        tilemap = TileMap(tile_data=data, tileset_surface=None)

        player_spawn_raw = data.get("player_spawn", {"x": 0, "y": 0})
        companion_spawn_raw = data.get("companion_spawn", {"x": 0, "y": 0})

        return LevelData(
            tilemap=tilemap,
            entities=data.get("entities", []),
            triggers=data.get("triggers", []),
            parallax_layers=data.get("parallax", []),
            metadata=data.get("metadata", {}),
            player_spawn=(player_spawn_raw["x"], player_spawn_raw["y"]),
            companion_spawn=(companion_spawn_raw["x"], companion_spawn_raw["y"]),
        )
