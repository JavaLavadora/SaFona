"""Tests for the LevelLoader."""

import pytest

from sa_fona.config.settings import DATA_DIR
from sa_fona.level.level_loader import LevelData, LevelLoader
from sa_fona.level.tilemap import TILE_SIZE


@pytest.fixture
def level_data() -> LevelData:
    """Load the test level."""
    loader = LevelLoader()
    path = str(DATA_DIR / "levels" / "test" / "test_level.json")
    return loader.load(path)


class TestLevelLoaderBasics:
    """Basic loading tests."""

    def test_loads_without_error(self) -> None:
        loader = LevelLoader()
        path = str(DATA_DIR / "levels" / "test" / "test_level.json")
        data = loader.load(path)
        assert data is not None

    def test_returns_level_data_instance(self, level_data: LevelData) -> None:
        assert isinstance(level_data, LevelData)


class TestLevelDataContents:
    """Verify contents of loaded LevelData."""

    def test_player_spawn(self, level_data: LevelData) -> None:
        assert level_data.player_spawn == (2, 12)

    def test_companion_spawn(self, level_data: LevelData) -> None:
        assert level_data.companion_spawn == (3, 12)

    def test_tilemap_dimensions(self, level_data: LevelData) -> None:
        assert level_data.tilemap.width_tiles == 60
        assert level_data.tilemap.height_tiles == 15

    def test_tilemap_pixel_dimensions(self, level_data: LevelData) -> None:
        assert level_data.tilemap.width_pixels == 60 * TILE_SIZE
        assert level_data.tilemap.height_pixels == 15 * TILE_SIZE

    def test_entities_is_list(self, level_data: LevelData) -> None:
        assert isinstance(level_data.entities, list)

    def test_triggers_is_list(self, level_data: LevelData) -> None:
        assert isinstance(level_data.triggers, list)

    def test_metadata_has_name(self, level_data: LevelData) -> None:
        assert level_data.metadata.get("name") == "Test Level"

    def test_tilemap_has_solid_ground(self, level_data: LevelData) -> None:
        """The bottom row should have solid tiles."""
        solid_rects = level_data.tilemap.get_collision_rects("solid")
        assert len(solid_rects) > 0

    def test_tilemap_has_one_way_platforms(self, level_data: LevelData) -> None:
        one_way_rects = level_data.tilemap.get_collision_rects("one_way")
        assert len(one_way_rects) > 0

    def test_tilemap_has_hazard_tiles(self, level_data: LevelData) -> None:
        hazard_rects = level_data.tilemap.get_collision_rects("hazard")
        assert len(hazard_rects) > 0
