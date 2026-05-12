"""Tests for the PhysicsSystem."""

import pygame
import pytest

from sa_fona.level.tilemap import TILE_SIZE, TileMap
from sa_fona.systems.physics import PhysicsSystem


@pytest.fixture
def flat_ground_data() -> dict:
    """A 10x5 level with a solid ground row at row 4."""
    return {
        "dimensions": {"width": 10, "height": 5},
        "layers": {
            "midground": [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
        },
        "collision_types": {"solid": [1], "one_way": [10]},
    }


@pytest.fixture
def one_way_data() -> dict:
    """A 10x8 level with a one-way platform at row 4 and ground at row 7."""
    return {
        "dimensions": {"width": 10, "height": 8},
        "layers": {
            "midground": [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 10, 10, 10, 10, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
        },
        "collision_types": {"solid": [1], "one_way": [10]},
    }


@pytest.fixture
def wall_data() -> dict:
    """A 10x5 level with a wall column and ground."""
    return {
        "dimensions": {"width": 10, "height": 5},
        "layers": {
            "midground": [
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
        },
        "collision_types": {"solid": [1], "one_way": [10]},
    }


class TestGravity:
    """Tests that gravity accelerates downward velocity."""

    def test_gravity_increases_vy(self, flat_ground_data: dict) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap, gravity=800.0)

        # Place entity high up (row 0), no collisions expected.
        rect = pygame.Rect(0, 0, 16, 16)
        vel = [0.0, 0.0]
        _, vel, _ = physics.update_rect(rect, vel, 0.016, False)
        assert vel[1] > 0.0, "Gravity should increase vy"

    def test_gravity_property(self, flat_ground_data: dict) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap, gravity=500.0)
        assert physics.gravity == 500.0


class TestSolidGround:
    """Tests that entities land on solid ground."""

    def test_entity_stops_on_ground(self, flat_ground_data: dict) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap, gravity=800.0)

        # Place entity above the ground and let it fall for multiple frames.
        ground_y = 4 * TILE_SIZE
        rect = pygame.Rect(0, ground_y - 32, 16, 16)
        vel = [0.0, 0.0]
        on_ground = False

        for _ in range(60):
            rect, vel, on_ground = physics.update_rect(rect, vel, 0.016, on_ground)

        assert rect.bottom <= ground_y + 1, "Entity should land on ground"
        assert on_ground, "Entity should be on_ground after landing"

    def test_entity_does_not_fall_through(self, flat_ground_data: dict) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap, gravity=800.0)

        ground_y = 4 * TILE_SIZE
        rect = pygame.Rect(16, ground_y - 20, 16, 16)
        vel = [0.0, 0.0]
        on_ground = False

        # Simulate many frames.
        for _ in range(120):
            rect, vel, on_ground = physics.update_rect(rect, vel, 0.016, on_ground)

        assert rect.bottom <= ground_y + 1, "Entity must not fall through ground"


class TestOneWayPlatforms:
    """Tests for one-way platform collision."""

    def test_lands_on_one_way_when_falling(self, one_way_data: dict) -> None:
        tilemap = TileMap(one_way_data)
        physics = PhysicsSystem(tilemap, gravity=800.0)

        platform_y = 4 * TILE_SIZE  # One-way at row 4.
        # Start well above the platform so the entity has time to fall.
        rect = pygame.Rect(2 * TILE_SIZE, 0, 16, 16)
        vel = [0.0, 0.0]
        on_ground = False

        for _ in range(120):
            rect, vel, on_ground = physics.update_rect(rect, vel, 0.016, on_ground)

        assert rect.bottom <= platform_y + 1, "Should land on one-way platform"
        assert on_ground

    def test_passes_through_from_below(self, one_way_data: dict) -> None:
        tilemap = TileMap(one_way_data)
        physics = PhysicsSystem(tilemap, gravity=0.0)  # No gravity for this test.

        platform_y = 4 * TILE_SIZE
        # Start below the platform with strong upward velocity.
        rect = pygame.Rect(2 * TILE_SIZE, platform_y + TILE_SIZE + 4, 16, 16)
        vel = [0.0, -900.0]

        rect, vel, _ = physics.update_rect(rect, vel, 0.05, False)
        # Should have moved upward through the platform.
        assert rect.top < platform_y, "Should pass through one-way from below"


class TestHorizontalCollision:
    """Tests for horizontal collision with walls."""

    def test_stops_at_wall_moving_right(self, wall_data: dict) -> None:
        tilemap = TileMap(wall_data)
        physics = PhysicsSystem(tilemap, gravity=0.0)

        wall_x = 4 * TILE_SIZE
        # Place entity to the left of the wall with rightward velocity.
        rect = pygame.Rect(wall_x - 20, 0, 16, 16)
        vel = [500.0, 0.0]

        rect, vel, _ = physics.update_rect(rect, vel, 0.016, False)
        assert rect.right <= wall_x + 1, "Should stop at wall"
        assert vel[0] == 0.0, "Horizontal velocity should be zeroed"

    def test_stops_at_wall_moving_left(self, wall_data: dict) -> None:
        tilemap = TileMap(wall_data)
        physics = PhysicsSystem(tilemap, gravity=0.0)

        wall_right = 4 * TILE_SIZE + TILE_SIZE
        # Place entity to the right of the wall with leftward velocity.
        rect = pygame.Rect(wall_right + 4, 0, 16, 16)
        vel = [-500.0, 0.0]

        rect, vel, _ = physics.update_rect(rect, vel, 0.016, False)
        assert rect.left >= wall_right - 1, "Should stop at wall"
        assert vel[0] == 0.0


class TestCheckCollision:
    """Tests for the check_collision query method."""

    def test_check_collision_returns_overlapping(self, flat_ground_data: dict) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap)

        # Rect overlapping the ground row.
        ground_y = 4 * TILE_SIZE
        rect = pygame.Rect(0, ground_y - 4, 20, 20)
        hits = physics.check_collision(rect, "solid")
        assert len(hits) > 0

    def test_check_collision_returns_empty_when_no_overlap(
        self, flat_ground_data: dict
    ) -> None:
        tilemap = TileMap(flat_ground_data)
        physics = PhysicsSystem(tilemap)

        rect = pygame.Rect(0, 0, 16, 16)
        hits = physics.check_collision(rect, "solid")
        assert len(hits) == 0
