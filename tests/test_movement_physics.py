"""Tests for wall contact filtering and crouch/crawl mechanics.

Covers:
1. Floating platforms (1 tile tall) do NOT report wall contact.
2. Thick walls (3+ tiles tall) DO report wall contact.
3. Pressing down reduces player hitbox height (crouch).
4. Pressing down + direction moves at reduced speed (crawl).
5. Cannot stand up when blocked by a ceiling above.
"""

import pygame
import pytest

from sa_fona.config.settings import (
    PLAYER_CRAWL_SPEED_FACTOR,
    PLAYER_CROUCH_HEIGHT,
    PLAYER_HEIGHT,
    PLAYER_MOVE_SPEED,
    PLAYER_WALL_CHECK_MARGIN,
    PLAYER_WIDTH,
)
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import Player, PlayerState
from sa_fona.level.tilemap import TILE_SIZE, TileMap
from sa_fona.systems.physics import PhysicsSystem


# ── Helpers ───────────────────────────────────────────────────────


def _make_player(
    level_data: dict, x: float, y: float,
) -> tuple[Player, PhysicsSystem, TileMap]:
    """Create a player, physics system, and tilemap from level data."""
    tilemap = TileMap(level_data)
    physics = PhysicsSystem(tilemap, gravity=800.0)
    player = Player(x, y)
    return player, physics, tilemap


def _check_wall_contact_filtered(
    player: Player, physics: PhysicsSystem, tilemap: TileMap,
) -> tuple[bool, bool]:
    """Check wall contact using the same filtering logic as GameplayScene.

    Only reports wall contact for tiles that are part of a tall wall
    (at least 2 vertically stacked solid tiles).
    """
    margin = PLAYER_WALL_CHECK_MARGIN
    rect = player.rect
    solid_ids = tilemap._collision_types.get("solid", set())

    def _has_tall_wall(tile_rects: list[pygame.Rect]) -> bool:
        for tile_rect in tile_rects:
            col = tile_rect.x // TILE_SIZE
            row = tile_rect.y // TILE_SIZE
            tile_above = tilemap.get_tile_at(col, row - 1, "midground")
            tile_below = tilemap.get_tile_at(col, row + 1, "midground")
            if tile_above in solid_ids or tile_below in solid_ids:
                return True
        return False

    left_probe = pygame.Rect(
        rect.left - margin, rect.top + 2, margin, rect.height - 4,
    )
    left_hits = physics.check_collision(left_probe, "solid")
    wall_left = _has_tall_wall(left_hits)

    right_probe = pygame.Rect(
        rect.right, rect.top + 2, margin, rect.height - 4,
    )
    right_hits = physics.check_collision(right_probe, "solid")
    wall_right = _has_tall_wall(right_hits)

    return wall_left, wall_right


def _step(
    player: Player, physics: PhysicsSystem, tilemap: TileMap, dt: float,
) -> None:
    """Run one frame: update_intent -> physics -> post_physics."""
    player.update_intent(dt)
    player.rect, player.velocity, on_ground = physics.update_rect(
        player.rect, player.velocity, dt, player.on_ground,
    )
    wall_left, wall_right = _check_wall_contact_filtered(
        player, physics, tilemap,
    )
    player.post_physics(on_ground, wall_left, wall_right)


def _input(**kwargs) -> InputState:
    """Create an InputState with the given overrides."""
    return InputState(**kwargs)


def _settle_on_ground(
    player: Player,
    physics: PhysicsSystem,
    tilemap: TileMap,
    frames: int = 30,
) -> None:
    """Run the player for several frames with no input to settle on ground."""
    empty = _input()
    for _ in range(frames):
        player.handle_input(empty)
        _step(player, physics, tilemap, 1.0 / 60.0)


def _check_ceiling(player: Player, physics: PhysicsSystem) -> bool:
    """Check if standing up from crouch would hit a solid tile above."""
    if not player.is_crouched:
        return False
    height_diff = PLAYER_HEIGHT - PLAYER_CROUCH_HEIGHT
    probe = pygame.Rect(
        player.rect.left,
        player.rect.top - height_diff,
        player.rect.width,
        height_diff,
    )
    return len(physics.check_collision(probe, "solid")) > 0


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def floating_platform_level() -> dict:
    """10x10 level with a single-tile-tall floating platform at col 5, row 4."""
    rows = []
    for r in range(10):
        if r == 9:
            rows.append([1] * 10)  # ground
        elif r == 4:
            row = [0] * 10
            row[5] = 1  # single floating platform tile
            rows.append(row)
        else:
            rows.append([0] * 10)
    return {
        "dimensions": {"width": 10, "height": 10},
        "layers": {"midground": rows},
        "collision_types": {"solid": [1], "one_way": [10]},
    }


@pytest.fixture
def thick_wall_level() -> dict:
    """10x10 level with a 5-tile-tall wall at col 5 (rows 2-8)."""
    rows = []
    for r in range(10):
        if r == 9:
            rows.append([1] * 10)  # ground
        else:
            row = [0] * 10
            if 2 <= r <= 8:
                row[5] = 1  # tall wall column
            rows.append(row)
    return {
        "dimensions": {"width": 10, "height": 10},
        "layers": {"midground": rows},
        "collision_types": {"solid": [1], "one_way": [10]},
    }


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


# ── Task 1: Wall contact filtering tests ─────────────────────────


class TestWallContactFiltering:
    """Tests that wall contact is filtered by wall height."""

    def test_floating_platform_no_wall_contact(
        self, floating_platform_level: dict,
    ) -> None:
        """A single-tile-tall floating platform should NOT report wall contact."""
        # Platform tile at (col=5, row=4).
        # Player placed with right edge adjacent to tile left edge.
        px = 5 * TILE_SIZE - PLAYER_WIDTH
        py = 4 * TILE_SIZE
        player, physics, tilemap = _make_player(
            floating_platform_level, px, py,
        )
        player.rect.right = 5 * TILE_SIZE
        player.rect.y = 4 * TILE_SIZE

        wall_left, wall_right = _check_wall_contact_filtered(
            player, physics, tilemap,
        )
        assert not wall_right, (
            "Single-tile floating platform should NOT report wall contact"
        )

    def test_thick_wall_reports_wall_contact(
        self, thick_wall_level: dict,
    ) -> None:
        """A tall wall (5 tiles stacked) should report wall contact."""
        px = 5 * TILE_SIZE - PLAYER_WIDTH
        py = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(thick_wall_level, px, py)
        player.rect.right = 5 * TILE_SIZE
        player.rect.y = 5 * TILE_SIZE

        wall_left, wall_right = _check_wall_contact_filtered(
            player, physics, tilemap,
        )
        assert wall_right, (
            "Tall wall (5 tiles) should report wall contact on the right"
        )

    def test_two_stacked_tiles_report_wall_contact(self) -> None:
        """Two vertically stacked solid tiles should report wall contact."""
        rows = []
        for r in range(10):
            if r == 9:
                rows.append([1] * 10)
            elif r in (4, 5):
                row = [0] * 10
                row[5] = 1
                rows.append(row)
            else:
                rows.append([0] * 10)
        level_data = {
            "dimensions": {"width": 10, "height": 10},
            "layers": {"midground": rows},
            "collision_types": {"solid": [1], "one_way": [10]},
        }
        px = 5 * TILE_SIZE - PLAYER_WIDTH
        py = 4 * TILE_SIZE
        player, physics, tilemap = _make_player(level_data, px, py)
        player.rect.right = 5 * TILE_SIZE
        player.rect.y = 4 * TILE_SIZE

        wall_left, wall_right = _check_wall_contact_filtered(
            player, physics, tilemap,
        )
        assert wall_right, (
            "Two stacked solid tiles should report wall contact"
        )


# ── Task 2: Crouch and crawl tests ───────────────────────────────


class TestCrouch:
    """Tests for crouching mechanics."""

    def test_crouch_reduces_height(self, flat_ground: dict) -> None:
        """Pressing down while on ground should reduce the player's
        hitbox height to PLAYER_CROUCH_HEIGHT."""
        ground_y = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(
            flat_ground, 32, ground_y - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)

        assert player.rect.height == PLAYER_HEIGHT
        original_bottom = player.rect.bottom

        # Press down to crouch.
        player._ceiling_blocked = False
        player.handle_input(_input(move_down=True))
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert player.rect.height == PLAYER_CROUCH_HEIGHT, (
            f"Crouching should reduce height to {PLAYER_CROUCH_HEIGHT}, "
            f"got {player.rect.height}"
        )
        assert player.rect.bottom == original_bottom, (
            "Bottom edge should stay the same when crouching"
        )
        assert player.state == PlayerState.CROUCHING

    def test_crouch_state_while_stationary(self, flat_ground: dict) -> None:
        """Crouching without horizontal input should enter CROUCHING state."""
        ground_y = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(
            flat_ground, 32, ground_y - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)

        player._ceiling_blocked = False
        player.handle_input(_input(move_down=True))
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert player.state == PlayerState.CROUCHING


class TestCrawl:
    """Tests for crawling mechanics."""

    def test_crawl_moves_at_reduced_speed(self, flat_ground: dict) -> None:
        """Pressing down + direction should move at reduced speed."""
        ground_y = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(
            flat_ground, 48, ground_y - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)

        # Enter crouch.
        player._ceiling_blocked = False
        player.handle_input(_input(move_down=True))
        _step(player, physics, tilemap, 1.0 / 60.0)

        # Now crawl right.
        x_before = player.rect.x
        player._ceiling_blocked = False
        player.handle_input(
            _input(move_down=True, move_right=True, move_x=1.0),
        )
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert player.state == PlayerState.CRAWLING
        expected_speed = PLAYER_MOVE_SPEED * PLAYER_CRAWL_SPEED_FACTOR
        displacement = player.rect.x - x_before
        expected_disp = round(expected_speed * (1.0 / 60.0))
        assert abs(displacement - expected_disp) <= 1, (
            f"Crawl displacement {displacement} should be ~{expected_disp} "
            f"(crawl speed = {expected_speed})"
        )

    def test_crawl_state(self, flat_ground: dict) -> None:
        """Pressing down + direction should enter CRAWLING state."""
        ground_y = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(
            flat_ground, 48, ground_y - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)

        player._ceiling_blocked = False
        player.handle_input(
            _input(move_down=True, move_right=True, move_x=1.0),
        )
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert player.state == PlayerState.CRAWLING


class TestCrouchCeiling:
    """Tests for ceiling blocking standup."""

    def test_cannot_stand_up_under_low_ceiling(self) -> None:
        """If a solid tile is above, releasing down should keep the
        player crouched.

        Level layout (12 rows):
          - Row 7: ceiling tile at columns 2-6.
          - Row 9: full ground.
          - Player starts at column 0 (no ceiling above), settles on ground,
            then is repositioned under the ceiling to test standup blocking.

        Ground top at y=144.  Ceiling row 7 occupies y=112..128.
        Player crouched: bottom=144, top=124, height=20.
        Standing probe: height_diff=12, probe top=124-12=112, covers [112,124).
        Ceiling tile: [112,128). Overlap exists -> blocked.
        """
        custom_rows = [[0] * 10 for _ in range(12)]
        custom_rows[9] = [1] * 10  # ground
        custom_rows[7] = [0, 0, 1, 1, 1, 1, 1, 0, 0, 0]  # ceiling
        level_data = {
            "dimensions": {"width": 10, "height": 12},
            "layers": {"midground": custom_rows},
            "collision_types": {"solid": [1], "one_way": [10]},
        }

        # Start the player at column 0 where there is no ceiling above.
        player, physics, tilemap = _make_player(
            level_data, 0, 9 * TILE_SIZE - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)
        assert player.on_ground

        # Crouch in open space (column 0, no ceiling).
        player._ceiling_blocked = False
        player.handle_input(_input(move_down=True))
        _step(player, physics, tilemap, 1.0 / 60.0)
        assert player.is_crouched

        # Move the player under the ceiling (column 3).
        player.rect.x = 3 * TILE_SIZE

        # Verify the ceiling blocks standup.
        blocked = _check_ceiling(player, physics)
        assert blocked, (
            "Standing up should be blocked when a solid tile is above"
        )

        # Release down with ceiling flagged -> should stay crouched.
        player._ceiling_blocked = blocked
        player.handle_input(_input())  # no down pressed
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert player.is_crouched, (
            "Player should remain crouched when ceiling blocks standing up"
        )

    def test_can_stand_up_in_open_space(self, flat_ground: dict) -> None:
        """In open space, releasing down should restore standing height."""
        ground_y = 5 * TILE_SIZE
        player, physics, tilemap = _make_player(
            flat_ground, 48, ground_y - PLAYER_HEIGHT,
        )
        _settle_on_ground(player, physics, tilemap)

        # Crouch.
        player._ceiling_blocked = False
        player.handle_input(_input(move_down=True))
        _step(player, physics, tilemap, 1.0 / 60.0)
        assert player.is_crouched

        # Release down in open space.
        player._ceiling_blocked = _check_ceiling(player, physics)
        assert not player._ceiling_blocked, "No ceiling in flat ground level"
        player.handle_input(_input())
        _step(player, physics, tilemap, 1.0 / 60.0)

        assert not player.is_crouched, "Should stand up when ceiling is clear"
        assert player.rect.height == PLAYER_HEIGHT
