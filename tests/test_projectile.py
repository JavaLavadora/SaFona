"""Tests for the Projectile entity: movement, range, and collision hooks."""

import pygame
import pytest

from sa_fona.entities.projectile import Projectile, ProjectileType


@pytest.fixture
def basic_projectile() -> Projectile:
    """Create a basic right-moving projectile."""
    return Projectile(
        x=100,
        y=100,
        width=8,
        height=8,
        direction=1.0,
        speed=250.0,
        damage=2.0,
        charge_tier=1,
        max_range=128.0,
    )


@pytest.fixture
def left_projectile() -> Projectile:
    """Create a left-moving projectile."""
    return Projectile(
        x=200,
        y=100,
        width=8,
        height=8,
        direction=-1.0,
        speed=250.0,
        damage=1.0,
        charge_tier=1,
        max_range=128.0,
    )


class TestProjectileInit:
    """Tests for projectile initialization."""

    def test_position(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.rect.x == 100
        assert basic_projectile.rect.y == 100

    def test_size(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.rect.width == 8
        assert basic_projectile.rect.height == 8

    def test_damage(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.damage == 2.0

    def test_charge_tier(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.charge_tier == 1

    def test_type(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.projectile_type == ProjectileType.BASIC_STONE

    def test_starts_active(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.active is True

    def test_distance_starts_zero(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.distance_travelled == 0.0

    def test_velocity_right(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.velocity[0] == 250.0
        assert basic_projectile.velocity[1] == 0.0

    def test_velocity_left(self, left_projectile: Projectile) -> None:
        assert left_projectile.velocity[0] == -250.0

    def test_facing_right(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.facing_right is True

    def test_facing_left(self, left_projectile: Projectile) -> None:
        assert left_projectile.facing_right is False

    def test_has_sprite(self, basic_projectile: Projectile) -> None:
        assert basic_projectile.sprite is not None


class TestProjectileMovement:
    """Tests for projectile movement."""

    def test_moves_right(self, basic_projectile: Projectile) -> None:
        """Projectile should move right when direction is positive."""
        initial_x = basic_projectile.rect.x
        basic_projectile.update(1 / 60)
        assert basic_projectile.rect.x > initial_x

    def test_moves_left(self, left_projectile: Projectile) -> None:
        """Projectile should move left when direction is negative."""
        initial_x = left_projectile.rect.x
        left_projectile.update(1 / 60)
        assert left_projectile.rect.x < initial_x

    def test_no_vertical_movement(self, basic_projectile: Projectile) -> None:
        """Projectile should not move vertically (no gravity on projectiles)."""
        initial_y = basic_projectile.rect.y
        basic_projectile.update(1 / 60)
        assert basic_projectile.rect.y == initial_y

    def test_distance_tracks(self, basic_projectile: Projectile) -> None:
        """Distance travelled should accumulate."""
        basic_projectile.update(1 / 60)
        assert basic_projectile.distance_travelled > 0

    def test_distance_is_absolute(self, left_projectile: Projectile) -> None:
        """Distance should be positive even for left-moving projectiles."""
        left_projectile.update(1 / 60)
        assert left_projectile.distance_travelled > 0


class TestProjectileRange:
    """Tests for projectile range limit."""

    def test_active_within_range(self, basic_projectile: Projectile) -> None:
        """Projectile should remain active when within range."""
        basic_projectile.update(1 / 60)
        assert basic_projectile.active is True

    def test_deactivated_at_max_range(self) -> None:
        """Projectile should deactivate when max range is exceeded."""
        proj = Projectile(
            x=0, y=0, width=8, height=8,
            direction=1.0, speed=1000.0, damage=1.0,
            charge_tier=1, max_range=50.0,
        )
        # Update enough frames to exceed 50px range at 1000 px/s.
        for _ in range(10):
            proj.update(1 / 60)
        assert proj.active is False

    def test_short_range_projectile(self) -> None:
        """Very short range projectiles should deactivate quickly."""
        proj = Projectile(
            x=0, y=0, width=8, height=8,
            direction=1.0, speed=250.0, damage=1.0,
            charge_tier=1, max_range=5.0,
        )
        # At 250 px/s, need ~2 frames (each ~4.17 px) to exceed 5 px.
        proj.update(1 / 60)
        proj.update(1 / 60)
        assert proj.active is False


class TestProjectileCollisionHooks:
    """Tests for collision hook methods."""

    def test_on_hit_tile_deactivates(self, basic_projectile: Projectile) -> None:
        """Default on_hit_tile should deactivate the projectile."""
        basic_projectile.on_hit_tile()
        assert basic_projectile.active is False

    def test_on_hit_entity_deactivates(self, basic_projectile: Projectile) -> None:
        """Default on_hit_entity should deactivate the projectile."""
        # Create a dummy entity-like object for testing.
        from sa_fona.entities.player import Player
        dummy = Player(0, 0)
        basic_projectile.on_hit_entity(dummy)
        assert basic_projectile.active is False


class TestProjectileRendering:
    """Tests for projectile rendering (should not crash)."""

    def test_render_does_not_crash(self, basic_projectile: Projectile) -> None:
        surface = pygame.Surface((384, 216))
        basic_projectile.render(surface, (0, 0))

    def test_render_with_camera_offset(self, basic_projectile: Projectile) -> None:
        surface = pygame.Surface((384, 216))
        basic_projectile.render(surface, (50, 30))
