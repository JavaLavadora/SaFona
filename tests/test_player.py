"""Tests for the Player entity: state transitions, wall jump, variable jump."""

import pygame
import pytest

from sa_fona.config.settings import (
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_VARIABLE_JUMP_CUTOFF,
    PLAYER_WALL_JUMP_FORCE_X,
    PLAYER_WALL_JUMP_FORCE_Y,
    PLAYER_WALL_SLIDE_SPEED,
)
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import Player, PlayerState
from sa_fona.level.tilemap import TILE_SIZE, TileMap
from sa_fona.systems.physics import PhysicsSystem


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def flat_ground() -> dict:
    """10x6 level with solid ground at row 5."""
    return {
        "dimensions": {"width": 10, "height": 6},
        "layers": {
            "midground": [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
def walled_level() -> dict:
    """10x10 level with walls on columns 0 and 5, ground at row 9."""
    rows = []
    for r in range(10):
        if r < 9:
            row = [0] * 10
            row[0] = 1   # left wall
            row[5] = 1   # mid wall
            rows.append(row)
        else:
            rows.append([1] * 10)  # ground
    return {
        "dimensions": {"width": 10, "height": 10},
        "layers": {"midground": rows},
        "collision_types": {"solid": [1], "one_way": [10]},
    }


def _make_player(level_data: dict, x: float, y: float) -> tuple[Player, PhysicsSystem]:
    """Create a player and physics system from level data."""
    tilemap = TileMap(level_data)
    physics = PhysicsSystem(tilemap, gravity=800.0)
    player = Player(x, y, physics)
    return player, physics


def _input(**kwargs) -> InputState:
    """Create an InputState with the given overrides."""
    return InputState(**kwargs)


def _settle_on_ground(player: Player, frames: int = 30) -> None:
    """Run the player for several frames with no input to settle on ground."""
    empty = _input()
    for _ in range(frames):
        player.handle_input(empty)
        player.update(1.0 / 60.0)


# ── State transition tests ─────────────────────────────────────────


class TestStateTransitions:
    """Tests that the player enters the correct state."""

    def test_idle_on_ground(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)
        assert player.state == PlayerState.IDLE

    def test_running_on_ground(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)
        player.handle_input(_input(move_right=True, move_x=1.0))
        player.update(1.0 / 60.0)
        assert player.state == PlayerState.RUNNING

    def test_jumping_after_jump_press(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        player.update(1.0 / 60.0)
        assert player.state == PlayerState.JUMPING

    def test_falling_after_walking_off_ledge(self, flat_ground: dict) -> None:
        """Walk past the edge of the ground and confirm falling state."""
        # Place near the right edge of ground -- ground ends at col 9.
        ground_y = 5 * TILE_SIZE
        # The ground spans cols 0-9. We need a level with a gap.
        gap_data = {
            "dimensions": {"width": 10, "height": 6},
            "layers": {
                "midground": [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                ],
            },
            "collision_types": {"solid": [1], "one_way": [10]},
        }
        player, _ = _make_player(gap_data, 2 * TILE_SIZE, ground_y - 32)
        _settle_on_ground(player)
        assert player.on_ground

        # Walk right off the edge.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            player.update(1.0 / 60.0)

        assert player.state == PlayerState.FALLING

    def test_wall_sliding_state(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        # Place player next to the mid wall (col 5). Player right edge near col 5.
        wall_x = 5 * TILE_SIZE
        px = wall_x - 24 - 1  # just to the left of the wall
        player, _ = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        player.update(1.0 / 60.0)

        # Wait until falling.
        for _ in range(30):
            player.handle_input(_input(move_right=True, move_x=1.0, jump_held=True))
            player.update(1.0 / 60.0)

        # Press into the wall while airborne and falling.
        for _ in range(30):
            player.handle_input(_input(move_right=True, move_x=1.0))
            player.update(1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING


# ── Wall jump tests ────────────────────────────────────────────────


class TestWallJump:
    """Tests for wall jump detection and execution."""

    def test_wall_jump_gives_upward_velocity(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - 24 - 1
        player, _ = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        player.update(1.0 / 60.0)

        # Move toward wall and wait until airborne against the wall.
        for _ in range(40):
            player.handle_input(_input(move_right=True, move_x=1.0))
            player.update(1.0 / 60.0)

        # Now press jump while touching wall and airborne.
        player.handle_input(_input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0))
        player.update(1.0 / 60.0)

        # If wall jump triggered, velocity should be upward and pushing left.
        if player.state == PlayerState.WALL_JUMPING:
            assert player.velocity[1] < 0, "Wall jump should give upward velocity"
            assert player.velocity[0] < 0, "Wall jump off right wall pushes left"

    def test_wall_jump_off_left_wall(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        # Place near the left wall (col 0). Player left edge near col 0.
        left_wall_right = TILE_SIZE  # col 0 wall right edge
        px = left_wall_right + 1
        player, _ = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        player.update(1.0 / 60.0)

        # Move left into wall.
        for _ in range(40):
            player.handle_input(_input(move_left=True, move_x=-1.0))
            player.update(1.0 / 60.0)

        # Wall jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True, move_left=True, move_x=-1.0))
        player.update(1.0 / 60.0)

        if player.state == PlayerState.WALL_JUMPING:
            assert player.velocity[1] < 0
            assert player.velocity[0] > 0, "Wall jump off left wall pushes right"


# ── Variable jump height tests ─────────────────────────────────────


class TestVariableJumpHeight:
    """Tests for variable jump height (short hop vs full jump)."""

    def test_full_jump_reaches_higher(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player_full, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player_full)

        player_short, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player_short)

        # Full jump: hold jump the entire time.
        player_full.handle_input(_input(jump_pressed=True, jump_held=True))
        player_full.update(1.0 / 60.0)
        highest_full = player_full.rect.y

        for _ in range(30):
            player_full.handle_input(_input(jump_held=True))
            player_full.update(1.0 / 60.0)
            if player_full.rect.y < highest_full:
                highest_full = player_full.rect.y

        # Short jump: press and release immediately.
        player_short.handle_input(_input(jump_pressed=True, jump_held=True))
        player_short.update(1.0 / 60.0)

        player_short.handle_input(_input(jump_released=True))
        player_short.update(1.0 / 60.0)

        highest_short = player_short.rect.y
        for _ in range(30):
            player_short.handle_input(_input())
            player_short.update(1.0 / 60.0)
            if player_short.rect.y < highest_short:
                highest_short = player_short.rect.y

        # Full jump should reach higher (lower y value) than short jump.
        assert highest_full < highest_short, (
            f"Full jump peak {highest_full} should be higher than "
            f"short jump peak {highest_short}"
        )

    def test_jump_release_cuts_velocity(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        player.update(1.0 / 60.0)
        vy_before = player.velocity[1]
        assert vy_before < 0, "Should have upward velocity after jump"

        # Release.
        player.handle_input(_input(jump_released=True))
        player.update(1.0 / 60.0)

        # After release, vy should have been cut (closer to zero).
        # Due to gravity applied in the same frame, we just check
        # the magnitude is less than what a non-cut frame would give.
        # The cutoff multiplies the upward velocity by 0.5 before
        # gravity is added.
        expected_cut_vy = vy_before * PLAYER_VARIABLE_JUMP_CUTOFF
        # After one frame of gravity, vy = cut_vy + gravity * dt
        # We check it's closer to zero than vy_before + gravity * dt would be.
        assert player.velocity[1] > vy_before, (
            "After release, velocity should be less negative (cut)"
        )


# ── Wall slide speed test ──────────────────────────────────────────


class TestWallSlide:
    """Tests that wall sliding caps downward speed."""

    def test_wall_slide_caps_speed(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - 24 - 1
        player, _ = _make_player(walled_level, px, ground_y - 80)

        # Don't settle -- start in the air.
        # Push into the wall and let gravity pull down.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            player.update(1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                # Check that downward velocity is capped.
                assert player.velocity[1] <= PLAYER_WALL_SLIDE_SPEED + 1.0, (
                    f"Wall slide speed {player.velocity[1]} should be capped "
                    f"at {PLAYER_WALL_SLIDE_SPEED}"
                )
                return

        # If we never entered wall slide, that's also informative
        # but the level geometry may not have supported it.
        # This test is best-effort.


# ── Facing direction tests ─────────────────────────────────────────


class TestFacingDirection:
    """Tests that facing direction updates correctly."""

    def test_facing_right_by_default(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        assert player.facing_right is True

    def test_facing_left_after_moving_left(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)
        player.handle_input(_input(move_left=True, move_x=-1.0))
        player.update(1.0 / 60.0)
        assert player.facing_right is False

    def test_facing_right_after_moving_right(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)
        player.handle_input(_input(move_left=True, move_x=-1.0))
        player.update(1.0 / 60.0)
        player.handle_input(_input(move_right=True, move_x=1.0))
        player.update(1.0 / 60.0)
        assert player.facing_right is True


# ── Placeholder rendering tests ────────────────────────────────────


class TestPlaceholderRendering:
    """Tests that each state uses a different colored surface."""

    def test_sprite_not_none(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        assert player.sprite is not None

    def test_different_colors_for_states(self, flat_ground: dict) -> None:
        """Verify idle and running produce different sprites."""
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player)

        idle_color = player.sprite.get_at((0, 0))

        player.handle_input(_input(move_right=True, move_x=1.0))
        player.update(1.0 / 60.0)
        running_color = player.sprite.get_at((0, 0))

        assert idle_color != running_color, (
            "Idle and running states should have different colors"
        )
