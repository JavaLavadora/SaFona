"""Tests for enemy wall-facing adjustment and wall-ahead detection.

Verifies that enemies spawned next to walls face away from the wall,
that the correct facing direction survives behavior update ticks, and
that patrolling enemies reverse direction when hitting a wall mid-patrol.
"""

from __future__ import annotations

import pygame
import pytest

from sa_fona.entities.enemy import Enemy
from sa_fona.entities.enemy_behaviors import EnemyBehavior, PatrolBehavior
from sa_fona.level.tilemap import TILE_SIZE, TileMap


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


def _make_tilemap(width: int, height: int, midground: list[list[int]]) -> TileMap:
    """Build a TileMap from a midground grid.

    Args:
        width: Grid width in tiles.
        height: Grid height in tiles.
        midground: 2D list of tile IDs (1 = solid, 0 = air).

    Returns:
        A configured TileMap instance.
    """
    empty = [[0] * width for _ in range(height)]
    return TileMap({
        "dimensions": {"width": width, "height": height},
        "layers": {
            "background": [row[:] for row in empty],
            "midground": midground,
            "foreground": [row[:] for row in empty],
        },
        "collision_types": {
            "solid": [1],
            "one_way": [],
            "hazard": [],
        },
    })


def _make_corridor_tilemap(width: int = 8, height: int = 6) -> TileMap:
    """Build a tilemap shaped like a corridor with walls on both sides.

    Layout (8 wide, 6 tall):
        Row 0: 1 0 0 0 0 0 0 1   <- ceiling / walls
        Row 1: 1 0 0 0 0 0 0 1   <- walls
        Row 2: 1 0 0 0 0 0 0 1   <- walls
        Row 3: 1 0 0 0 0 0 0 1   <- walls (enemy body level)
        Row 4: 1 0 0 0 0 0 0 1   <- walls (enemy body level)
        Row 5: 1 1 1 1 1 1 1 1   <- ground

    Walls at col 0 and col (width-1) go from floor to ceiling.
    """
    midground = []
    for r in range(height - 1):
        row = [0] * width
        row[0] = 1              # left wall
        row[width - 1] = 1      # right wall
        midground.append(row)
    midground.append([1] * width)  # ground row
    return _make_tilemap(width, height, midground)


def _make_enemy(x: float, y: float) -> Enemy:
    """Create a patrol enemy (possessed_sheep style) at pixel coords.

    Args:
        x: Spawn X in pixels.
        y: Spawn Y in pixels.

    Returns:
        An Enemy with PatrolBehavior.
    """
    definition = {
        "display_name": "Test Sheep",
        "health": 2,
        "contact_damage": 0.5,
        "behavior": "patrol",
        "behavior_params": {
            "patrol_range": 5,
            "speed": 40,
            "charge_speed": 120,
            "charge_tell_time": 0.5,
            "charge_distance": 3,
            "attack_range": 2.0,
            "attack_cooldown": 2.0,
        },
        "hitbox": {"w": 16, "h": 16},
        "drops": {"stones": {"min": 1, "max": 2}, "heart_chance": 0.1},
    }
    return Enemy(x, y, "possessed_sheep", definition)


def _snap_enemy(enemy: Enemy, ground_row: int) -> None:
    """Simulate snap_to_ground by setting rect.bottom to the top of ground.

    Args:
        enemy: The enemy to snap.
        ground_row: The tile row of the ground.
    """
    enemy.rect.bottom = ground_row * TILE_SIZE
    enemy._sub_x = float(enemy.rect.x)


class TestAdjustFacingForWalls:
    """Tests for Enemy.adjust_facing_for_walls()."""

    def test_wall_on_right_faces_left(self):
        """Enemy next to a right wall should face left."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Spawn enemy at tile col 6 (next to right wall at col 7).
        # Ground is row 5; snap to ground.
        enemy = _make_enemy(6 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right is False, (
            "Enemy near right wall should face left"
        )

    def test_wall_on_left_faces_right(self):
        """Enemy next to a left wall should face right."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Spawn at tile col 1 (next to left wall at col 0).
        enemy = _make_enemy(1 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right is True, (
            "Enemy near left wall should face right"
        )

    def test_no_walls_keeps_default(self):
        """Enemy in open space (no walls at body level) should keep default."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Spawn in the middle at tile col 4 - far from walls.
        enemy = _make_enemy(4 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right is True, (
            "Enemy away from walls should keep default right facing"
        )

    def test_walls_both_sides_keeps_default(self):
        """Enemy with walls on both sides should keep default (right)."""
        # Narrow 4-tile corridor with walls.
        tilemap = _make_corridor_tilemap(width=4, height=6)

        # Spawn at tile col 1 - walls at col 0 (left) and col 3 (right).
        # center_tx = 1, left_tx = 0 (wall), right_tx = 2 (air).
        # Actually col 3 is 2 tiles away, not adjacent.
        # Use a 3-tile wide corridor instead:
        midground = []
        for r in range(5):
            midground.append([1, 0, 1])
        midground.append([1, 1, 1])
        tilemap = _make_tilemap(3, 6, midground)

        enemy = _make_enemy(1 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        enemy.adjust_facing_for_walls(tilemap)

        # Both walls detected, so default facing is kept.
        assert enemy.facing_right is True

    def test_platform_tiles_are_not_walls(self):
        """Ground platform tiles at foot level should NOT be detected as
        walls.  Only tiles at body level (above ground) count.

        This tests the level 1-3 scenario where sheep are ON a wide
        platform -- the platform surface tiles to the left and right
        are ground, not walls.
        """
        # Wide platform: ground on row 5 from col 2-10, walls at 0 and 13.
        width, height = 14, 7
        midground = []
        for r in range(height - 1):
            row = [0] * width
            row[0] = 1    # left wall column
            row[13] = 1   # right wall column
            midground.append(row)
        # Ground row has a wide platform.
        ground_row = [0] * width
        ground_row[0] = 1
        ground_row[13] = 1
        for c in range(2, 11):
            ground_row[c] = 1
        midground.append(ground_row)

        tilemap = _make_tilemap(width, height, midground)

        # Enemy at col 5 (middle of platform, walls far away).
        enemy = _make_enemy(5 * TILE_SIZE, 4 * TILE_SIZE)
        _snap_enemy(enemy, 6)

        enemy.adjust_facing_for_walls(tilemap)

        # No walls at body level (only at col 0 and 13).
        assert enemy.facing_right is True, (
            "Platform surface tiles must not be detected as walls"
        )

    def test_facing_survives_first_update_tick(self):
        """After adjust_facing_for_walls, the first behavior update
        should maintain the corrected facing direction."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Enemy near right wall -> should face left.
        enemy = _make_enemy(6 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)
        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right is False

        # Simulate update ticks (player far away, not in attack range).
        player_rect = pygame.Rect(0, 4 * TILE_SIZE, 24, 32)
        for _ in range(10):
            enemy.update_with_player(player_rect, 1 / 60, tilemap=tilemap)

        # The behavior's direction should still be -1.0 after initial set,
        # and facing_right should reflect movement to the left.
        assert enemy.behavior._direction == -1.0 or enemy.facing_right is False

    def test_behavior_direction_set_correctly(self):
        """set_initial_direction should update behavior _direction."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Near right wall.
        enemy = _make_enemy(6 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        # Before adjustment, default direction is right.
        assert enemy.behavior._direction == 1.0

        enemy.adjust_facing_for_walls(tilemap)

        # After adjustment, direction should be left.
        assert enemy.behavior._direction == -1.0

    def test_first_update_move_x_respects_direction(self):
        """The first behavior update should produce move_x matching
        the initial direction set by adjust_facing_for_walls."""
        tilemap = _make_corridor_tilemap(width=10, height=6)

        # Enemy near right wall at col 8 (next to wall at col 9).
        enemy = _make_enemy(8 * TILE_SIZE, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)
        enemy.adjust_facing_for_walls(tilemap)

        # First update tick - player far away.
        player_rect = pygame.Rect(0, 4 * TILE_SIZE, 24, 32)
        enemy.update_with_player(player_rect, 1 / 60, tilemap=tilemap)

        # After the first tick, the enemy should be moving left.
        assert enemy.facing_right is False, (
            "First update tick must respect initial direction (left)"
        )

    def test_level_1_3_sheep_at_col_23_not_near_wall(self):
        """In level 1-3, sheep at tile (23, 22) is on a wide platform
        (cols 15-27).  The right wall is at col 27 but the sheep is at
        col 23 -- 4 tiles away.  It should NOT have facing changed.
        """
        width, height = 28, 26
        midground = []
        for r in range(height):
            row = [0] * width
            row[0] = 1    # left wall
            row[27] = 1   # right wall
            midground.append(row)

        # Ground platform: row 24, cols 15-27 solid.
        for c in range(15, 28):
            midground[24][c] = 1

        tilemap = _make_tilemap(width, height, midground)

        enemy = _make_enemy(23 * TILE_SIZE, 22 * TILE_SIZE)
        _snap_enemy(enemy, 24)

        enemy.adjust_facing_for_walls(tilemap)

        # Not adjacent to wall -- col 24 (right_tx) is air at body level.
        assert enemy.facing_right is True

    def test_level_1_3_sheep_near_border_wall(self):
        """In a level 1-3 like layout, a sheep at col 26 on a platform
        that ends at the right wall (col 27) should face left.

        The right wall at col 27 extends from ceiling to floor.
        """
        width, height = 28, 26
        midground = []
        for r in range(height):
            row = [0] * width
            row[0] = 1    # left wall (full height)
            row[27] = 1   # right wall (full height)
            midground.append(row)

        # Ground at row 24, cols 15-27.
        for c in range(15, 28):
            midground[24][c] = 1

        tilemap = _make_tilemap(width, height, midground)

        # Sheep one tile from right border wall.
        enemy = _make_enemy(26 * TILE_SIZE, 22 * TILE_SIZE)
        _snap_enemy(enemy, 24)

        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right is False, (
            "Sheep one tile from right wall should face left"
        )

    def test_set_initial_direction_on_base_class(self):
        """set_initial_direction works on any behavior with _direction."""
        from sa_fona.entities.enemy_behaviors import ChaseBehavior

        chase = ChaseBehavior({"chase_range": 6, "speed": 50})
        chase.reset(100.0)

        # ChaseBehavior does not have _direction, so set_initial_direction
        # should be a no-op and not raise.
        chase.set_initial_direction(-1.0)

    def test_set_initial_direction_on_patrol(self):
        """set_initial_direction updates PatrolBehavior._direction."""
        patrol = PatrolBehavior({"patrol_range": 5, "speed": 40})
        patrol.reset(100.0)

        assert patrol._direction == 1.0
        patrol.set_initial_direction(-1.0)
        assert patrol._direction == -1.0


class TestCheckWallAhead:
    """Tests for EnemyBehavior.check_wall_ahead()."""

    def test_detects_wall_on_right(self):
        """check_wall_ahead returns True when solid tile is ahead (right)."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Enemy at col 6, ground row 5.  Wall at col 7.
        # Rect: x=96, y=48, w=16, h=16 -> right=112, bottom=64.
        # Probe x = 113 -> tile_x = 7 (wall).
        enemy_rect = pygame.Rect(6 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        assert EnemyBehavior.check_wall_ahead(enemy_rect, 1.0, tilemap) is True

    def test_detects_wall_on_left(self):
        """check_wall_ahead returns True when solid tile is ahead (left)."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Enemy at col 1.  Wall at col 0.
        enemy_rect = pygame.Rect(1 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        assert EnemyBehavior.check_wall_ahead(enemy_rect, -1.0, tilemap) is True

    def test_no_wall_in_open_space(self):
        """check_wall_ahead returns False when no solid tile ahead."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Enemy at col 4 -- open space in both directions.
        enemy_rect = pygame.Rect(4 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        assert EnemyBehavior.check_wall_ahead(enemy_rect, 1.0, tilemap) is False
        assert EnemyBehavior.check_wall_ahead(enemy_rect, -1.0, tilemap) is False

    def test_no_tilemap_returns_false(self):
        """check_wall_ahead returns False when tilemap is None."""
        enemy_rect = pygame.Rect(4 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        assert EnemyBehavior.check_wall_ahead(enemy_rect, 1.0, None) is False


class TestPatrolWallReversal:
    """Tests that patrol enemies reverse direction when hitting a wall."""

    def test_patrol_reverses_at_right_wall(self):
        """A patrolling sheep reverses when it reaches the right wall."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Place enemy so its rect.right is right next to the wall at col 7.
        # Wall starts at pixel 7*16=112.  With HITBOX_SHRINK=2 the rect
        # is 12px wide.  We need rect.right close to 112 so probe hits
        # tile 7.  rect.right = rect.x + 12.  If rect.x = 99 then
        # right = 111, probe = 112, tile = 7.  spawn_x = 99 - 2 = 97.
        enemy = _make_enemy(97, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)

        assert enemy.behavior._direction == 1.0  # default: right

        # Simulate a tick with player far away.
        player_rect = pygame.Rect(0, 4 * TILE_SIZE, 24, 32)
        enemy.behavior.update(enemy.rect, player_rect, 1 / 60, tilemap=tilemap)

        # check_wall_ahead should have reversed the direction.
        assert enemy.behavior._direction == -1.0, (
            "Sheep should reverse direction when wall is ahead"
        )

    def test_patrol_reverses_at_left_wall(self):
        """A patrolling sheep reverses when it reaches the left wall."""
        tilemap = _make_corridor_tilemap(width=8, height=6)

        # Place enemy so its rect.left is right next to the wall at col 0.
        # Wall ends at pixel 1*16=16.  With HITBOX_SHRINK=2, rect.x = 16
        # (spawn_x=14), rect.left = 16, probe = 15, tile = 0 (wall).
        enemy = _make_enemy(14, 3 * TILE_SIZE)
        _snap_enemy(enemy, 5)
        enemy.behavior.set_initial_direction(-1.0)

        player_rect = pygame.Rect(7 * TILE_SIZE, 4 * TILE_SIZE, 24, 32)
        enemy.behavior.update(enemy.rect, player_rect, 1 / 60, tilemap=tilemap)

        assert enemy.behavior._direction == 1.0, (
            "Sheep should reverse direction when left wall is ahead"
        )

    def test_sheep_col23_wall_col27_not_stuck(self):
        """Level 1-3 scenario: sheep spawns at col 23, patrols right, hits
        wall at col 27.  After enough update ticks, the sheep must NOT be
        stuck facing right -- it should reverse at the wall.

        Platform: row 24, cols 15-27 solid.  Right wall column at 27
        extends full height.
        """
        width, height = 28, 26
        midground = []
        for r in range(height):
            row = [0] * width
            row[0] = 1    # left wall
            row[27] = 1   # right wall (full height)
            midground.append(row)

        # Ground platform: row 24, cols 15-27 solid.
        for c in range(15, 28):
            midground[24][c] = 1

        tilemap = _make_tilemap(width, height, midground)

        # Sheep at col 23, snapped to ground row 24.
        enemy = _make_enemy(23 * TILE_SIZE, 22 * TILE_SIZE)
        _snap_enemy(enemy, 24)
        enemy.behavior.reset(23 * TILE_SIZE)

        player_rect = pygame.Rect(0, 0, 24, 32)  # Far away

        # Simulate 300 ticks (5 seconds at 60fps).  The sheep should
        # walk right, hit the wall at col 27, and reverse.
        for _ in range(300):
            result = enemy.behavior.update(
                enemy.rect, player_rect, 1 / 60, tilemap=tilemap
            )
            # Apply movement to simulate actual patrol.
            if result.move_x != 0.0 and result.speed > 0:
                dx = result.move_x * result.speed * (1 / 60)
                enemy.rect.x += int(dx)
                enemy._sub_x = float(enemy.rect.x)

        # The sheep should have reversed at least once.  Its direction
        # should NOT be stuck at 1.0 if it reached the wall.
        # Check that it's NOT at or past the wall.
        assert enemy.rect.right <= 27 * TILE_SIZE, (
            "Sheep should not be inside or past the wall"
        )
        # The sheep should have reversed at some point (not stuck).
        # After 300 ticks of walking, if it reversed, it should be
        # somewhere to the left of the wall.
        assert enemy.rect.x < 26 * TILE_SIZE, (
            "Sheep should have reversed and walked away from the wall"
        )
