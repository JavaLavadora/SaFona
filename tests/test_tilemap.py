"""Tests for the TileMap class."""

import pygame
import pytest

from sa_fona.level.tilemap import TILE_SIZE, TileMap


@pytest.fixture
def sample_tile_data() -> dict:
    """Minimal tile data for a 4x3 grid."""
    return {
        "dimensions": {"width": 4, "height": 3},
        "layers": {
            "background": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            "midground": [
                [0, 0, 0, 0],
                [0, 1, 10, 0],
                [1, 1, 1, 40],
            ],
            "foreground": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        },
        "collision_types": {
            "solid": [1, 2, 3],
            "one_way": [10, 11],
            "hazard": [40],
        },
    }


@pytest.fixture
def tilemap(sample_tile_data: dict) -> TileMap:
    """Create a TileMap from sample data."""
    return TileMap(sample_tile_data)


class TestTileMapLoad:
    """Tests for loading a TileMap from data."""

    def test_loads_without_error(self, sample_tile_data: dict) -> None:
        tilemap = TileMap(sample_tile_data)
        assert tilemap is not None

    def test_width_tiles(self, tilemap: TileMap) -> None:
        assert tilemap.width_tiles == 4

    def test_height_tiles(self, tilemap: TileMap) -> None:
        assert tilemap.height_tiles == 3

    def test_width_pixels(self, tilemap: TileMap) -> None:
        assert tilemap.width_pixels == 4 * TILE_SIZE

    def test_height_pixels(self, tilemap: TileMap) -> None:
        assert tilemap.height_pixels == 3 * TILE_SIZE


class TestCollisionRects:
    """Tests for get_collision_rects."""

    def test_solid_rects_count(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("solid")
        # Row 1 has one solid (1,1), row 2 has three solids (0,2), (1,2), (2,2)
        assert len(rects) == 4

    def test_solid_rects_are_correct_size(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("solid")
        for r in rects:
            assert r.width == TILE_SIZE
            assert r.height == TILE_SIZE

    def test_solid_rect_position(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("solid")
        # (1,1) tile should be at pixel (16, 16)
        positions = [(r.x, r.y) for r in rects]
        assert (1 * TILE_SIZE, 1 * TILE_SIZE) in positions

    def test_one_way_rects(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("one_way")
        assert len(rects) == 1
        assert rects[0].x == 2 * TILE_SIZE
        assert rects[0].y == 1 * TILE_SIZE

    def test_hazard_rects(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("hazard")
        assert len(rects) == 1
        assert rects[0].x == 3 * TILE_SIZE
        assert rects[0].y == 2 * TILE_SIZE

    def test_unknown_layer_returns_empty(self, tilemap: TileMap) -> None:
        rects = tilemap.get_collision_rects("nonexistent")
        assert rects == []


class TestTileAccessors:
    """Tests for get_tile_at and set_tile_at."""

    def test_get_tile_at_returns_correct_id(self, tilemap: TileMap) -> None:
        assert tilemap.get_tile_at(1, 1, "midground") == 1

    def test_get_tile_at_empty(self, tilemap: TileMap) -> None:
        assert tilemap.get_tile_at(0, 0, "midground") == 0

    def test_get_tile_at_one_way(self, tilemap: TileMap) -> None:
        assert tilemap.get_tile_at(2, 1, "midground") == 10

    def test_get_tile_at_out_of_bounds(self, tilemap: TileMap) -> None:
        assert tilemap.get_tile_at(99, 99, "midground") == 0

    def test_get_tile_at_missing_layer(self, tilemap: TileMap) -> None:
        assert tilemap.get_tile_at(0, 0, "nonexistent") == 0

    def test_set_tile_at_changes_value(self, tilemap: TileMap) -> None:
        tilemap.set_tile_at(0, 0, "midground", 5)
        assert tilemap.get_tile_at(0, 0, "midground") == 5

    def test_set_tile_at_missing_layer_raises(self, tilemap: TileMap) -> None:
        with pytest.raises(KeyError):
            tilemap.set_tile_at(0, 0, "nonexistent", 1)

    def test_set_tile_at_out_of_bounds_raises(self, tilemap: TileMap) -> None:
        with pytest.raises(IndexError):
            tilemap.set_tile_at(99, 99, "midground", 1)
