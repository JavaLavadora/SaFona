"""Tests for the TileMap class."""

import pygame
import pytest

from sa_fona.level.tilemap import (
    HIGHLIGHT_COLOR_CAVE,
    HIGHLIGHT_COLOR_OUTDOOR,
    TILE_SIZE,
    TileMap,
)


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


class TestIsSolidAt:
    """Tests for the is_solid_at convenience method."""

    def test_solid_tile_returns_true(self, tilemap: TileMap) -> None:
        """A tile with a solid collision ID should be solid."""
        # (1,1) in midground is tile ID 1, which is in the solid set.
        assert tilemap.is_solid_at(1, 1) is True

    def test_empty_tile_returns_false(self, tilemap: TileMap) -> None:
        """An empty tile (ID 0) should not be solid."""
        assert tilemap.is_solid_at(0, 0) is False

    def test_one_way_tile_is_not_solid(self, tilemap: TileMap) -> None:
        """A one-way platform tile should not count as solid."""
        # (2,1) in midground is tile ID 10 (one_way).
        assert tilemap.is_solid_at(2, 1) is False

    def test_hazard_tile_is_not_solid(self, tilemap: TileMap) -> None:
        """A hazard tile should not count as solid."""
        # (3,2) in midground is tile ID 40 (hazard).
        assert tilemap.is_solid_at(3, 2) is False

    def test_out_of_bounds_returns_false(self, tilemap: TileMap) -> None:
        """Out-of-bounds positions should return False (air)."""
        assert tilemap.is_solid_at(99, 99) is False

    def test_solid_bottom_row(self, tilemap: TileMap) -> None:
        """Bottom row solid tiles should be detected."""
        # Row 2: [1, 1, 1, 40] — cols 0,1,2 are solid (ID 1).
        assert tilemap.is_solid_at(0, 2) is True
        assert tilemap.is_solid_at(1, 2) is True
        assert tilemap.is_solid_at(2, 2) is True


class TestHighlightColor:
    """Tests for the top-edge highlight color selection."""

    def test_default_highlight_is_outdoor(self, tilemap: TileMap) -> None:
        """Without tileset metadata, default highlight is outdoor (warm)."""
        assert tilemap._highlight_color == HIGHLIGHT_COLOR_OUTDOOR

    def test_cave_tileset_uses_cave_highlight(self, sample_tile_data: dict) -> None:
        """A tileset containing 'cave' should use the cave (cool) highlight."""
        sample_tile_data["metadata"] = {"tileset": "world1_cave"}
        tm = TileMap(sample_tile_data)
        assert tm._highlight_color == HIGHLIGHT_COLOR_CAVE

    def test_talayot_tileset_uses_outdoor_highlight(self, sample_tile_data: dict) -> None:
        """A talayot tileset (no 'cave') should use the outdoor (warm) highlight."""
        sample_tile_data["metadata"] = {"tileset": "world1_talayot"}
        tm = TileMap(sample_tile_data)
        assert tm._highlight_color == HIGHLIGHT_COLOR_OUTDOOR

    def test_outdoor_tileset_uses_outdoor_highlight(self, sample_tile_data: dict) -> None:
        """An outdoor tileset should use the outdoor (warm) highlight."""
        sample_tile_data["metadata"] = {"tileset": "world1"}
        tm = TileMap(sample_tile_data)
        assert tm._highlight_color == HIGHLIGHT_COLOR_OUTDOOR


class TestRenderLayerHighlight:
    """Tests for the 1px top-edge highlight on exposed midground tiles."""

    def test_render_midground_does_not_crash(self, tilemap: TileMap) -> None:
        """Rendering the midground layer should not crash."""
        surface = pygame.Surface((4 * TILE_SIZE, 3 * TILE_SIZE))
        tilemap.render_layer(surface, "midground", (0, 0))

    def test_highlight_drawn_on_exposed_top_edge(self, sample_tile_data: dict) -> None:
        """A tile with air above should have its top-left pixel highlighted."""
        tm = TileMap(sample_tile_data)
        surface = pygame.Surface((4 * TILE_SIZE, 3 * TILE_SIZE))
        surface.fill((0, 0, 0))
        tm.render_layer(surface, "midground", (0, 0))

        # Tile (1, 1) has air above (row 0 col 1 = 0).
        # The top-left pixel should be the highlight color.
        pixel = surface.get_at((1 * TILE_SIZE, 1 * TILE_SIZE))
        assert (pixel.r, pixel.g, pixel.b) == HIGHLIGHT_COLOR_OUTDOOR

    def test_no_highlight_when_tile_above_is_solid(self, sample_tile_data: dict) -> None:
        """A tile with a solid tile above should NOT have a highlight."""
        tm = TileMap(sample_tile_data)
        surface = pygame.Surface((4 * TILE_SIZE, 3 * TILE_SIZE))
        surface.fill((0, 0, 0))
        tm.render_layer(surface, "midground", (0, 0))

        # Tile (1, 2) has tile (1, 1)=1 above — not empty.
        # The top-left pixel should be the tile color, not highlight.
        pixel = surface.get_at((1 * TILE_SIZE, 2 * TILE_SIZE))
        assert (pixel.r, pixel.g, pixel.b) != HIGHLIGHT_COLOR_OUTDOOR

    def test_no_highlight_on_background_layer(self, tilemap: TileMap) -> None:
        """The background layer should NOT get top-edge highlights."""
        surface = pygame.Surface((4 * TILE_SIZE, 3 * TILE_SIZE))
        surface.fill((0, 0, 0))
        tilemap.render_layer(surface, "background", (0, 0))
        # Background is all zeros — nothing rendered, surface stays black.
        pixel = surface.get_at((0, 0))
        assert (pixel.r, pixel.g, pixel.b) == (0, 0, 0)
