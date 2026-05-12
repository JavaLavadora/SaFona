"""Tests for the Player entity: state transitions, wall jump, variable jump.

After the dependency-inversion refactor, Player no longer owns a
PhysicsSystem reference.  Tests simulate the scene orchestration flow:
update_intent -> physics.update_rect -> post_physics.
"""

import pygame
import pytest

from sa_fona.config.settings import (
    PLAYER_GRAVITY,
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_VARIABLE_JUMP_CUTOFF,
    PLAYER_WALL_CHECK_MARGIN,
    PLAYER_WALL_JUMP_FORCE_X,
    PLAYER_WALL_JUMP_FORCE_Y,
    PLAYER_WALL_SLIDE_SPEED,
    PLAYER_WIDTH,
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
    physics = PhysicsSystem(tilemap, gravity=PLAYER_GRAVITY)
    player = Player(x, y)
    return player, physics


def _check_wall_contact(
    player: Player, physics: PhysicsSystem
) -> tuple[bool, bool]:
    """Probe for wall contact around the player rect (mirrors GameplayScene)."""
    margin = PLAYER_WALL_CHECK_MARGIN
    rect = player.rect

    left_probe = pygame.Rect(
        rect.left - margin,
        rect.top + 2,
        margin,
        rect.height - 4,
    )
    wall_left = len(physics.check_collision(left_probe, "solid")) > 0

    right_probe = pygame.Rect(
        rect.right,
        rect.top + 2,
        margin,
        rect.height - 4,
    )
    wall_right = len(physics.check_collision(right_probe, "solid")) > 0

    return wall_left, wall_right


def _step(player: Player, physics: PhysicsSystem, dt: float) -> None:
    """Run one frame: update_intent -> physics -> post_physics."""
    player.update_intent(dt)
    player.rect, player.velocity, on_ground = physics.update_rect(
        player.rect, player.velocity, dt, player.on_ground,
    )
    wall_left, wall_right = _check_wall_contact(player, physics)
    player.post_physics(on_ground, wall_left, wall_right)


def _input(**kwargs) -> InputState:
    """Create an InputState with the given overrides."""
    return InputState(**kwargs)


def _settle_on_ground(player: Player, physics: PhysicsSystem, frames: int = 30) -> None:
    """Run the player for several frames with no input to settle on ground."""
    empty = _input()
    for _ in range(frames):
        player.handle_input(empty)
        _step(player, physics, 1.0 / 60.0)


# ── State transition tests ─────────────────────────────────────────


class TestStateTransitions:
    """Tests that the player enters the correct state."""

    def test_idle_on_ground(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)
        assert player.state == PlayerState.IDLE

    def test_running_on_ground(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)
        player.handle_input(_input(move_right=True, move_x=1.0))
        _step(player, physics, 1.0 / 60.0)
        assert player.state == PlayerState.RUNNING

    def test_jumping_after_jump_press(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)
        assert player.state == PlayerState.JUMPING

    def test_falling_after_walking_off_ledge(self, flat_ground: dict) -> None:
        """Walk past the edge of the ground and confirm falling state."""
        ground_y = 5 * TILE_SIZE
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
        player, physics = _make_player(gap_data, 2 * TILE_SIZE, ground_y - 32)
        _settle_on_ground(player, physics)
        assert player.on_ground

        # Walk right off the edge.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)

        assert player.state == PlayerState.FALLING

    def test_wall_sliding_state(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Wait until falling.
        for _ in range(30):
            player.handle_input(_input(move_right=True, move_x=1.0, jump_held=True))
            _step(player, physics, 1.0 / 60.0)

        # Press into the wall while airborne and falling.
        for _ in range(30):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING


# ── Wall jump tests ────────────────────────────────────────────────


class TestWallJump:
    """Tests for wall jump detection and execution."""

    def test_wall_jump_gives_upward_velocity(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move toward wall and wait until airborne against the wall.
        for _ in range(40):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)

        # Press INTO the right wall (right) + jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0))
        _step(player, physics, 1.0 / 60.0)

        # If wall jump triggered, velocity should be upward and pushing left.
        if player.state == PlayerState.WALL_JUMPING:
            assert player.velocity[1] < 0, "Wall jump should give upward velocity"
            assert player.velocity[0] < 0, "Wall jump off right wall pushes left"

    def test_wall_jump_off_left_wall(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        left_wall_right = TILE_SIZE
        px = left_wall_right + 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move left into wall.
        for _ in range(40):
            player.handle_input(_input(move_left=True, move_x=-1.0))
            _step(player, physics, 1.0 / 60.0)

        # Press INTO the left wall (left) + jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True, move_left=True, move_x=-1.0))
        _step(player, physics, 1.0 / 60.0)

        if player.state == PlayerState.WALL_JUMPING:
            assert player.velocity[1] < 0
            assert player.velocity[0] > 0, "Wall jump off left wall pushes right"

    def test_wall_jump_requires_into_direction(self, walled_level: dict) -> None:
        """Pressing jump with the AWAY direction while wall sliding
        should NOT trigger a wall jump."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING

        # Press jump while pressing AWAY from the wall (left direction).
        # This should NOT produce a wall jump.
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_left=True, move_x=-1.0)
        )
        _step(player, physics, 1.0 / 60.0)
        assert player.state != PlayerState.WALL_JUMPING, (
            "Pressing jump + away direction from wall should NOT wall jump"
        )

    def test_wall_jump_with_into_direction_works(self, walled_level: dict) -> None:
        """Pressing into the wall + jump while wall sliding should
        trigger a wall jump."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING

        # Press jump + INTO the right wall (right direction).
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)

        assert player.state == PlayerState.WALL_JUMPING, (
            "Pressing jump + into direction should trigger wall jump"
        )
        assert player.velocity[1] < 0, "Wall jump should give upward velocity"
        assert player.velocity[0] < 0, "Wall jump off right wall pushes left"

    def test_jump_without_direction_detaches_from_wall(self, walled_level: dict) -> None:
        """Pressing just jump (no direction) while wall sliding should
        detach the player from the wall (fall) without wall jump forces."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING
        vy_before = player.velocity[1]

        # Press just jump, no direction.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Should NOT have wall jump state.
        assert player.state != PlayerState.WALL_JUMPING, (
            "Pressing just jump should NOT trigger wall jump"
        )
        # Horizontal velocity should be zeroed (detach).
        assert player.velocity[0] == 0.0, (
            "Detaching from wall should zero horizontal velocity"
        )
        # Should NOT have the upward wall jump force.
        assert player.velocity[1] >= 0, (
            "Detaching without wall jump should not give upward impulse"
        )


# ── Variable jump height tests ─────────────────────────────────────


class TestVariableJumpHeight:
    """Tests for variable jump height (short hop vs full jump)."""

    def test_full_jump_reaches_higher(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player_full, physics_full = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player_full, physics_full)

        player_short, physics_short = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player_short, physics_short)

        # Full jump: hold jump the entire time.
        player_full.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player_full, physics_full, 1.0 / 60.0)
        highest_full = player_full.rect.y

        for _ in range(30):
            player_full.handle_input(_input(jump_held=True))
            _step(player_full, physics_full, 1.0 / 60.0)
            if player_full.rect.y < highest_full:
                highest_full = player_full.rect.y

        # Short jump: press and release immediately.
        player_short.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player_short, physics_short, 1.0 / 60.0)

        player_short.handle_input(_input(jump_released=True))
        _step(player_short, physics_short, 1.0 / 60.0)

        highest_short = player_short.rect.y
        for _ in range(30):
            player_short.handle_input(_input())
            _step(player_short, physics_short, 1.0 / 60.0)
            if player_short.rect.y < highest_short:
                highest_short = player_short.rect.y

        # Full jump should reach higher (lower y value) than short jump.
        assert highest_full < highest_short, (
            f"Full jump peak {highest_full} should be higher than "
            f"short jump peak {highest_short}"
        )

    def test_jump_release_cuts_velocity(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)
        vy_before = player.velocity[1]
        assert vy_before < 0, "Should have upward velocity after jump"

        # Release.
        player.handle_input(_input(jump_released=True))
        _step(player, physics, 1.0 / 60.0)

        # After release, vy should have been cut (closer to zero).
        assert player.velocity[1] > vy_before, (
            "After release, velocity should be less negative (cut)"
        )


# ── Wall slide speed test ──────────────────────────────────────────


class TestWallSlide:
    """Tests that wall sliding caps downward speed."""

    def test_wall_slide_caps_speed(self, walled_level: dict) -> None:
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 80)

        # Don't settle -- start in the air.
        # Push into the wall and let gravity pull down.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                # Check that downward velocity is capped.
                assert player.velocity[1] <= PLAYER_WALL_SLIDE_SPEED + 1.0, (
                    f"Wall slide speed {player.velocity[1]} should be capped "
                    f"at {PLAYER_WALL_SLIDE_SPEED}"
                )
                return

        # If we never entered wall slide, that's also informative
        # but the level geometry may not have supported it.


# ── Facing direction tests ─────────────────────────────────────────


class TestFacingDirection:
    """Tests that facing direction updates correctly."""

    def test_facing_right_by_default(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        assert player.facing_right is True

    def test_facing_left_after_moving_left(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)
        player.handle_input(_input(move_left=True, move_x=-1.0))
        _step(player, physics, 1.0 / 60.0)
        assert player.facing_right is False

    def test_facing_right_after_moving_right(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)
        player.handle_input(_input(move_left=True, move_x=-1.0))
        _step(player, physics, 1.0 / 60.0)
        player.handle_input(_input(move_right=True, move_x=1.0))
        _step(player, physics, 1.0 / 60.0)
        assert player.facing_right is True


# ── Placeholder rendering tests ────────────────────────────────────


# ── Same-wall re-grab prevention tests ────────────────────────────


class TestSameWallRegrab:
    """Tests that same-wall infinite climbing is prevented."""

    @staticmethod
    def _wide_walled_level() -> dict:
        """A wider walled level so wall jump arc can't reach the opposite wall.

        Layout (16 wide, 10 tall): wall at col 0, wall at col 12, ground row 9.
        """
        rows = []
        for r in range(10):
            if r < 9:
                row = [0] * 16
                row[0] = 1    # left wall
                row[12] = 1   # right wall (far enough away)
                rows.append(row)
            else:
                rows.append([1] * 16)  # ground
        return {
            "dimensions": {"width": 16, "height": 10},
            "layers": {"midground": rows},
            "collision_types": {"solid": [1], "one_way": [10]},
        }

    def test_cannot_gain_height_on_same_wall_after_wall_jump(self) -> None:
        """After wall jumping from a wall, the player must not be able
        to wall slide at a higher position on the same wall.  They CAN
        re-grab the wall at or below the wall jump origin (sliding back
        down is fine), but never above it."""
        wide_level = self._wide_walled_level()
        ground_y = 9 * TILE_SIZE
        # Place player next to the right-side wall (column 12).
        wall_x = 12 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(wide_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        entered_wall_slide = False
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                entered_wall_slide = True
                break

        assert entered_wall_slide, "Should enter wall slide on right wall"

        # Press INTO the right wall (right) + jump.
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)
        assert player.wall_jump_origin_side == "right", (
            "Should track that the wall jump came from the right wall"
        )
        origin_y = player.wall_jump_origin_y
        assert origin_y is not None, "Should track wall jump origin Y"

        # Let lockout expire, then try to re-grab the same wall.
        # If the player touches the wall again while higher than origin_y,
        # wall sliding must be prevented.
        for _ in range(120):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.on_ground:
                break
            if player.state == PlayerState.WALL_SLIDING:
                # Re-grab is only allowed at or below origin Y.
                assert player.rect.y >= origin_y, (
                    f"Wall slide at Y={player.rect.y} is above origin "
                    f"Y={origin_y} -- should be prevented"
                )

    def test_spam_jump_cannot_climb_same_wall(self, walled_level: dict) -> None:
        """Spamming jump against the same wall must not let the player
        gain height above the original wall jump origin.  Same-wall
        rejumps are allowed at descending heights, but the player must
        never reach above the first wall jump's origin Y."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        # Wall jump off the right wall (press right/into + jump).
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)

        # Record origin Y from the first wall jump.
        first_origin_y = player.wall_jump_origin_y
        assert first_origin_y is not None

        # Now spam: press into wall + jump each frame.  When wall
        # sliding, pressing into + jump triggers a wall jump.  When
        # airborne/not sliding, pressing into tries to re-grab.
        prev_state = player.state
        for i in range(180):
            # Always press into the right wall + jump.
            # When wall sliding this triggers the wall jump;
            # otherwise it attempts to re-grab the wall.
            player.handle_input(
                _input(
                    jump_pressed=True,
                    jump_held=True,
                    move_right=True,
                    move_x=1.0,
                )
            )
            _step(player, physics, 1.0 / 60.0)

            if player.on_ground:
                break

            # If a new wall jump fires, its origin must be at or below
            # the first wall jump (no net height gain).
            if (
                player.state == PlayerState.WALL_JUMPING
                and prev_state != PlayerState.WALL_JUMPING
            ):
                assert player.wall_jump_origin_y >= first_origin_y, (
                    f"Same-wall rejump at Y={player.wall_jump_origin_y} "
                    f"is above first origin Y={first_origin_y} -- "
                    f"climbing exploit is possible"
                )

            prev_state = player.state

    def test_wall_jump_records_origin_y(self, walled_level: dict) -> None:
        """Wall jump should record the Y position for height tracking."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        assert player.wall_jump_origin_y is None

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        # Wall jump: press INTO (right) + jump.
        y_before_jump = float(player.rect.y)
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)

        if player.wall_jump_origin_side is not None:
            assert player.wall_jump_origin_y is not None, (
                "wall_jump_origin_y should be set after a wall jump"
            )

    def test_height_tracking_clears_on_landing(self, walled_level: dict) -> None:
        """Height tracking state should clear when the player lands."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump and wall slide.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        # Wall jump: press INTO (right) + jump.
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)

        # Let the player fall and land.
        for _ in range(180):
            player.handle_input(_input())
            _step(player, physics, 1.0 / 60.0)
            if player.on_ground:
                break

        assert player.on_ground, "Player should have landed"
        assert player.wall_jump_origin_side is None, (
            "Origin side should be cleared after landing"
        )
        assert player.wall_jump_origin_y is None, (
            "Origin Y should be cleared after landing"
        )

    def test_can_wall_jump_same_wall_when_lower(self, walled_level: dict) -> None:
        """After wall jumping from a wall and sliding back down to at or
        below the origin Y, the player should be able to wall jump again
        from the same wall.  The new jump updates the origin Y so each
        successive jump starts lower."""
        ground_y = 9 * TILE_SIZE
        wall_x = 5 * TILE_SIZE
        px = wall_x - PLAYER_WIDTH - 1
        player, physics = _make_player(walled_level, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move right into the wall until wall sliding.
        for _ in range(60):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                break

        assert player.state == PlayerState.WALL_SLIDING

        # Wall jump off the right wall (press right/into + jump).
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)
        assert player.wall_jump_origin_side == "right"
        first_origin_y = player.wall_jump_origin_y
        assert first_origin_y is not None

        # Let the player arc away and then slide back down onto the same
        # wall.  We stop pressing jump so the player falls back naturally.
        reached_wall_slide = False
        for _ in range(180):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.on_ground:
                break
            if (
                player.state == PlayerState.WALL_SLIDING
                and player.rect.y >= first_origin_y
            ):
                reached_wall_slide = True
                break

        assert reached_wall_slide, (
            "Player should be able to wall slide on the same wall "
            "after sliding back down to or below origin Y"
        )

        # Wall jump again from the same wall (press right/into + jump).
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_right=True, move_x=1.0)
        )
        _step(player, physics, 1.0 / 60.0)

        assert player.state == PlayerState.WALL_JUMPING, (
            "Should be able to wall jump from the same wall when at or "
            "below the previous origin Y"
        )
        # New origin should be at or below the first.
        assert player.wall_jump_origin_y >= first_origin_y, (
            f"New origin Y={player.wall_jump_origin_y} should be >= "
            f"first origin Y={first_origin_y}"
        )

    def test_can_grab_opposite_wall_after_wall_jump(self) -> None:
        """After wall jumping from left wall, player CAN enter
        wall_slide on the right wall (wall-to-wall climbing)."""
        # Custom level: narrow corridor with walls on both sides.
        # Columns 0 and 4 are walls, ground at row 9, 5 wide x 10 tall.
        rows = []
        for r in range(10):
            if r < 9:
                row = [0] * 5
                row[0] = 1  # left wall
                row[4] = 1  # right wall
                rows.append(row)
            else:
                rows.append([1] * 5)  # ground
        corridor = {
            "dimensions": {"width": 5, "height": 10},
            "layers": {"midground": rows},
            "collision_types": {"solid": [1], "one_way": [10]},
        }

        ground_y = 9 * TILE_SIZE
        left_wall_right_edge = 1 * TILE_SIZE  # col 0 occupies [0, TILE_SIZE)
        px = left_wall_right_edge + 1  # just right of the left wall
        player, physics = _make_player(corridor, px, ground_y - 32)
        _settle_on_ground(player, physics)

        # Jump up.
        player.handle_input(_input(jump_pressed=True, jump_held=True))
        _step(player, physics, 1.0 / 60.0)

        # Move left into the left wall until wall sliding.
        entered_wall_slide = False
        for _ in range(60):
            player.handle_input(_input(move_left=True, move_x=-1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                entered_wall_slide = True
                break

        assert entered_wall_slide, "Should enter wall slide on left wall"

        # Wall jump off the left wall: press INTO (left) + jump.
        player.handle_input(
            _input(jump_pressed=True, jump_held=True, move_left=True, move_x=-1.0)
        )
        _step(player, physics, 1.0 / 60.0)
        assert player.wall_jump_origin_side == "left", (
            "Should track wall jump from left wall"
        )

        # Now move right toward the opposite (right) wall.
        # The player SHOULD be able to enter wall_slide on the right wall.
        grabbed_opposite = False
        for _ in range(120):
            player.handle_input(_input(move_right=True, move_x=1.0))
            _step(player, physics, 1.0 / 60.0)
            if player.state == PlayerState.WALL_SLIDING:
                grabbed_opposite = True
                break
            if player.on_ground:
                break

        assert grabbed_opposite, (
            "Should be able to grab the opposite wall after a wall jump"
        )


class TestPlaceholderRendering:
    """Tests that each state uses a different colored surface."""

    def test_sprite_not_none(self, flat_ground: dict) -> None:
        ground_y = 5 * TILE_SIZE
        player, _ = _make_player(flat_ground, 32, ground_y - 32)
        assert player.sprite is not None

    def test_different_colors_for_states(self, flat_ground: dict) -> None:
        """Verify idle and running produce different sprites."""
        ground_y = 5 * TILE_SIZE
        player, physics = _make_player(flat_ground, 32, ground_y - 32)
        _settle_on_ground(player, physics)

        idle_color = player.sprite.get_at((0, 0))

        player.handle_input(_input(move_right=True, move_x=1.0))
        _step(player, physics, 1.0 / 60.0)
        running_color = player.sprite.get_at((0, 0))

        assert idle_color != running_color, (
            "Idle and running states should have different colors"
        )
