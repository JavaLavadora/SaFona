"""Load a level from its JSON data file and produce runtime data."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from sa_fona.config.settings import ASSETS_DIR
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
        background: Optional background surface for the level.
    """

    tilemap: TileMap
    entities: list[dict] = field(default_factory=list)
    triggers: list[dict] = field(default_factory=list)
    parallax_layers: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    player_spawn: tuple[int, int] = (0, 0)
    companion_spawn: tuple[int, int] = (0, 0)
    background: pygame.Surface | None = None


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

        tileset_surface = self._load_tileset(data)
        tilemap = TileMap(tile_data=data, tileset_surface=tileset_surface)
        background_surface = self._load_background(data)

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
            background=background_surface,
        )

    @staticmethod
    def _load_tileset(data: dict) -> pygame.Surface | None:
        """Try to load the tileset PNG for the level's world.

        Returns None if the tileset file doesn't exist, allowing
        graceful fallback to placeholder colored rectangles.
        """
        metadata = data.get("metadata", {})
        tileset_id = metadata.get("tileset", "")
        if not tileset_id:
            return None
        tileset_path = ASSETS_DIR / "tilesets" / tileset_id / "tileset.png"
        if not tileset_path.is_file():
            return None
        try:
            return pygame.image.load(str(tileset_path)).convert_alpha()
        except pygame.error:
            return None

    @staticmethod
    def _load_background(data: dict) -> pygame.Surface | None:
        """Try to load the background image for the level.

        The metadata ``background`` field contains an identifier like
        ``"world1_bg"``.  The ``_bg`` suffix is stripped to find the
        actual file at ``assets/backgrounds/<base_name>.png``.

        Returns None if the background file doesn't exist or the
        identifier is empty/``"none"``, allowing graceful fallback
        to the procedural sky gradient.
        """
        metadata = data.get("metadata", {})
        bg_id = metadata.get("background", "")
        if not bg_id or bg_id == "none":
            return None

        # Strip the conventional ``_bg`` suffix if present.
        base_name = bg_id
        if base_name.endswith("_bg"):
            base_name = base_name[:-3]

        bg_path = ASSETS_DIR / "backgrounds" / f"{base_name}.png"
        if not bg_path.is_file():
            return None
        try:
            return pygame.image.load(str(bg_path)).convert()
        except pygame.error:
            return None
