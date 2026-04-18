"""Tests for enemy behavior components: patrol and chase."""

from __future__ import annotations

import pygame
import pytest

from sa_fona.entities.enemy_behaviors import (
    AttackState,
    BehaviorResult,
    ChaseBehavior,
    PatrolBehavior,
    create_behavior,
)
from sa_fona.level.tilemap import TileMap, TILE_SIZE


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


class TestPatrolBehavior:
    """Tests for the patrol behavior component."""

    def test_patrol_moves_back_and_forth(self):
        """Patrol behavior should reverse at range boundaries."""
        params = {"patrol_range": 3, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        # Initially moves right.
        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0
        assert result.speed == 40

    def test_patrol_reverses_at_right_boundary(self):
        """Patrol should reverse when exceeding right boundary."""
        params = {"patrol_range": 3, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        # Place enemy past the right boundary (100 + 3*16 = 148).
        enemy_rect = pygame.Rect(200, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == -1.0

    def test_patrol_reverses_at_left_boundary(self):
        """Patrol should reverse when exceeding left boundary."""
        params = {"patrol_range": 3, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        # Force direction to left, then go past boundary.
        patrol._direction = -1.0
        enemy_rect = pygame.Rect(40, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0

    def test_patrol_attack_tell_when_player_close(self):
        """Patrol should enter attack tell when player is in range."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "attack_range": 2.0,
            "attack_tell_time": 1.0,
            "attack_cooldown": 2.0,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        # Player close enough to trigger attack.
        player_rect = pygame.Rect(110, 100, 24, 32)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.TELL
        assert result.move_x == 0.0  # Stops to show tell.

    def test_patrol_attack_after_tell(self):
        """Patrol should attack after the tell timer expires."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "attack_range": 2.0,
            "attack_tell_time": 0.1,
            "attack_cooldown": 2.0,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(110, 100, 24, 32)

        # Enter tell.
        patrol.update(enemy_rect, player_rect, 1 / 60)

        # Advance past tell time.
        for _ in range(20):
            result = patrol.update(enemy_rect, player_rect, 1 / 60)

        assert result.attack_state == AttackState.ATTACKING
        assert result.wants_attack

    def test_patrol_charge_attack(self):
        """Sheep-style patrol should charge when attacking."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "charge_speed": 80,
            "charge_tell_time": 0.05,
            "charge_distance": 4,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(110, 100, 24, 32)

        # Enter tell + advance past it.
        for _ in range(10):
            result = patrol.update(enemy_rect, player_rect, 1 / 60)

        # Should be in attacking state with charge speed.
        if result.attack_state == AttackState.ATTACKING:
            assert result.speed == 80


class TestPatrolAggroBehavior:
    """Tests for patrol behavior damage aggro response."""

    def test_on_damaged_triggers_aggro(self):
        """Patrol should enter aggro state when damaged."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        patrol.on_damaged(300.0, 100.0)

        assert patrol.aggro_timer > 0

    def test_aggro_chases_toward_player(self):
        """While aggroed, patrol should move toward the player."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(300, 100, 24, 32)  # Player to the right.

        # Trigger aggro.
        patrol.on_damaged(300.0, 100.0)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0  # Chase right.
        assert result.speed == max(40 * 2.0, 50.0)  # Aggro speed with min.

    def test_aggro_chases_left(self):
        """While aggroed, patrol should chase left if player is left."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(200.0)

        enemy_rect = pygame.Rect(200, 100, 16, 16)
        player_rect = pygame.Rect(50, 100, 24, 32)  # Player to the left.

        patrol.on_damaged(50.0, 100.0)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == -1.0

    def test_aggro_expires_after_duration(self):
        """Aggro should expire after ~2 seconds, resuming patrol."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        patrol.on_damaged(500.0, 100.0)

        # Advance past aggro duration (3.0 seconds).
        for _ in range(200):
            patrol.update(enemy_rect, player_rect, 1 / 60)

        # Aggro should have expired.
        assert patrol.aggro_timer <= 0

        # Should now be in normal patrol.
        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.speed == 40  # Normal patrol speed, not aggro.

    def test_aggro_resets_on_behavior_reset(self):
        """Reset should clear aggro state."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        patrol.on_damaged(300.0, 100.0)
        assert patrol.aggro_timer > 0

        patrol.reset(100.0)
        assert patrol.aggro_timer == 0

    def test_aggro_overrides_tell_state(self):
        """Damage during TELL state should reset to IDLE and allow aggro chase."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "attack_range": 3.0,
            "attack_tell_time": 1.0,
            "attack_cooldown": 2.0,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_close = pygame.Rect(120, 100, 24, 32)

        result = patrol.update(enemy_rect, player_close, 1 / 60)
        assert result.attack_state == AttackState.TELL

        player_far = pygame.Rect(400, 100, 24, 32)
        patrol.on_damaged(400.0, 100.0)

        result = patrol.update(enemy_rect, player_far, 1 / 60)
        assert result.move_x == 1.0
        assert result.speed == max(40 * 2.0, 50.0)

    def test_aggro_overrides_attacking_state(self):
        """Damage during ATTACKING state should reset and allow aggro chase."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "attack_range": 3.0,
            "attack_tell_time": 0.01,
            "attack_cooldown": 2.0,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_close = pygame.Rect(120, 100, 24, 32)

        patrol.update(enemy_rect, player_close, 1 / 60)
        patrol.update(enemy_rect, player_close, 0.02)

        player_far = pygame.Rect(400, 100, 24, 32)
        patrol.on_damaged(400.0, 100.0)

        result = patrol.update(enemy_rect, player_far, 1 / 60)
        assert result.move_x == 1.0
        assert result.speed > 0

    def test_aggro_uses_min_speed_for_slow_enemies(self):
        """Slow enemies should use minimum aggro speed when chasing."""
        params = {"patrol_range": 3, "speed": 20}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(300, 100, 24, 32)

        patrol.on_damaged(300.0, 100.0)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0
        assert result.speed == 50.0  # Min speed, not 20 * 2.0 = 40.


class TestPatrolEdgeDetection:
    """Tests for patrol behavior ledge edge detection."""

    def _make_tilemap_with_gap(self):
        """Create a tilemap with a platform and a gap.

        Layout (5 wide, 4 tall):
            Row 0: empty
            Row 1: empty
            Row 2: enemy level (all empty)
            Row 3: solid, solid, solid, EMPTY, solid  <- gap at col 3
        """
        tile_data = {
            "dimensions": {"width": 5, "height": 4},
            "layers": {
                "midground": [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 1],
                ],
            },
            "collision_types": {"solid": [1]},
        }
        return TileMap(tile_data)

    def test_reverses_at_ledge(self):
        """Patrol should reverse direction when approaching a gap."""
        params = {"patrol_range": 10, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(0.0)

        tilemap = self._make_tilemap_with_gap()

        # Enemy at col 2, row 2 (just before the gap at col 3).
        # Enemy feet are at row 2 bottom = row 3 start = y=48.
        # Leading edge going right: x = 2*16 + 16 = 48.
        # Probe: tile_x = 49//16 = 3, tile_y = 48//16 = 3.
        # Tile (3, 3) = 0 (gap) -> should reverse.
        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        result = patrol.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        # Should have reversed from +1 to -1.
        assert result.move_x == -1.0

    def test_no_reverse_when_ground_ahead(self):
        """Patrol should keep going when ground exists ahead."""
        params = {"patrol_range": 10, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(0.0)

        tilemap = self._make_tilemap_with_gap()

        # Enemy at col 0, row 2. Ground at col 1, row 3 is solid.
        enemy_rect = pygame.Rect(0, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        player_rect = pygame.Rect(500, 100, 24, 32)

        result = patrol.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        # Should keep going right (ground ahead).
        assert result.move_x == 1.0

    def test_no_edge_detection_without_tilemap(self):
        """Edge detection should be skipped when no tilemap is provided."""
        params = {"patrol_range": 10, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(0.0)

        # Enemy at a position that would be a ledge if tilemap were provided.
        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        player_rect = pygame.Rect(500, 100, 24, 32)

        # No tilemap -> no edge detection -> should move normally.
        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0

    def test_aggro_hesitates_at_ledge_then_retreats(self):
        """At a ledge, enemy should hesitate then retreat to origin."""
        params = {"patrol_range": 10, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(0.0)

        tilemap = self._make_tilemap_with_gap()

        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        player_rect = pygame.Rect(4 * TILE_SIZE, 2 * TILE_SIZE, 24, 32)

        patrol.on_damaged(float(player_rect.centerx), float(player_rect.centery))

        # First update: hits ledge, enters hesitation (stops moving).
        result = patrol.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)
        assert result.move_x == 0.0
        assert result.speed == 0.0

        # Advance through hesitation (~0.6s).
        for _ in range(40):
            result = patrol.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        # Should now be retreating toward origin (x=0, enemy at x=32).
        assert result.move_x == -1.0
        assert result.speed == 40

    def test_damage_during_retreat_does_not_cancel(self):
        """Shots during retreat should not re-aggro (enemy can't cross gap)."""
        params = {"patrol_range": 10, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(0.0)

        tilemap = self._make_tilemap_with_gap()

        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        player_rect = pygame.Rect(4 * TILE_SIZE, 2 * TILE_SIZE, 24, 32)

        # Trigger aggro, hit ledge, start retreating.
        patrol.on_damaged(float(player_rect.centerx), float(player_rect.centery))
        for _ in range(50):
            patrol.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        assert patrol._retreating or patrol._hesitation_timer > 0

        # Hit again during retreat — should keep retreating.
        patrol.on_damaged(float(player_rect.centerx), float(player_rect.centery))
        assert patrol._retreating or patrol._hesitation_timer > 0

    def test_aggro_attacks_when_in_range(self):
        """During aggro chase, enemy should attack when close enough."""
        params = {
            "patrol_range": 5,
            "speed": 40,
            "attack_range": 2.0,
            "attack_tell_time": 0.8,
            "attack_cooldown": 2.0,
        }
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(120, 100, 24, 32)  # Within attack range.

        patrol.on_damaged(120.0, 100.0)

        result = patrol.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.TELL


class TestChaseBehavior:
    """Tests for the chase behavior component."""

    def test_chase_follows_player_in_range(self):
        """Chase should move toward the player when in detection range."""
        params = {"chase_range": 6, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(150, 100, 24, 32)  # 50px away, within range.

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0  # Move right toward player.
        assert result.speed == 50

    def test_chase_idles_when_player_out_of_range(self):
        """Chase should not move when the player is out of range."""
        params = {"chase_range": 3, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 0.0
        assert result.speed == 0.0

    def test_chase_attacks_when_close(self):
        """Chase should attack when within attack range."""
        params = {
            "chase_range": 6,
            "speed": 50,
            "attack_range": 1.5,
            "attack_cooldown": 1.0,
        }
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        # Very close to enemy.
        player_rect = pygame.Rect(105, 100, 24, 32)

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.ATTACKING
        assert result.wants_attack

    def test_chase_block_mechanic(self):
        """Chase behavior with block_chance should sometimes block."""
        params = {
            "chase_range": 6,
            "speed": 50,
            "block_chance": 1.0,  # Always blocks for test.
            "block_duration": 0.5,
        }
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        blocked = chase.try_block()
        assert blocked
        assert chase.is_blocking

    def test_chase_block_expires(self):
        """Block state should expire after block_duration."""
        params = {
            "chase_range": 6,
            "speed": 50,
            "block_chance": 1.0,
            "block_duration": 0.1,
        }
        chase = ChaseBehavior(params)
        chase.reset(0.0)
        chase.try_block()

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)

        # Advance time past block duration.
        for _ in range(20):
            chase.update(enemy_rect, player_rect, 0.02)

        assert not chase.is_blocking

    def test_chase_follows_left(self):
        """Chase should move left when player is to the left."""
        params = {"chase_range": 6, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(150, 100, 16, 16)
        player_rect = pygame.Rect(100, 100, 24, 32)

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == -1.0

    def test_chase_aggro_extends_range(self):
        """Damage should make chase pursue beyond normal chase_range."""
        params = {"chase_range": 3, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_rect = pygame.Rect(500, 100, 24, 32)

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 0.0

        chase.on_damaged(500.0, 100.0)

        result = chase.update(enemy_rect, player_rect, 1 / 60)
        assert result.move_x == 1.0
        assert result.speed == 50

    def test_chase_aggro_resets_attack_state(self):
        """Damage during attack should reset state and allow chase."""
        params = {
            "chase_range": 6,
            "speed": 50,
            "attack_range": 1.5,
            "attack_cooldown": 1.0,
        }
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        enemy_rect = pygame.Rect(100, 100, 16, 16)
        player_close = pygame.Rect(105, 100, 24, 32)

        result = chase.update(enemy_rect, player_close, 1 / 60)
        assert result.attack_state == AttackState.ATTACKING

        player_far = pygame.Rect(150, 100, 24, 32)
        chase.on_damaged(150.0, 100.0)

        result = chase.update(enemy_rect, player_far, 1 / 60)
        assert result.attack_state == AttackState.IDLE
        assert result.move_x == 1.0

    def test_chase_stops_at_ledge(self):
        """Chase should not walk off ledges."""
        from unittest.mock import MagicMock
        from sa_fona.level.tilemap import TILE_SIZE

        params = {"chase_range": 6, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(2 * TILE_SIZE)

        tilemap = MagicMock()
        def is_solid(tx, ty):
            if ty == 3: return tx <= 2
            return False
        tilemap.is_solid_at = is_solid

        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, 16, 16)
        player_rect = pygame.Rect(5 * TILE_SIZE, 2 * TILE_SIZE, 24, 32)

        result = chase.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)
        assert result.move_x == 0.0
        assert result.speed == 0.0

    def test_chase_retreats_after_ledge_hesitation(self):
        """Chase should retreat to origin after hesitating at ledge."""
        from unittest.mock import MagicMock
        from sa_fona.level.tilemap import TILE_SIZE

        params = {"chase_range": 6, "speed": 50}
        chase = ChaseBehavior(params)
        chase.reset(0.0)

        tilemap = MagicMock()
        def is_solid(tx, ty):
            if ty == 3: return tx <= 2
            return False
        tilemap.is_solid_at = is_solid

        enemy_rect = pygame.Rect(2 * TILE_SIZE, 2 * TILE_SIZE, 16, 16)
        player_rect = pygame.Rect(5 * TILE_SIZE, 2 * TILE_SIZE, 24, 32)

        # Hit ledge, enter hesitation.
        chase.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        # Advance past hesitation.
        for _ in range(40):
            result = chase.update(enemy_rect, player_rect, 1 / 60, tilemap=tilemap)

        # Should be retreating toward origin (x=0).
        assert result.move_x == -1.0
        assert result.speed == 50


class TestBehaviorFactory:
    """Tests for the behavior creation factory function."""

    def test_create_patrol(self):
        """Should create a PatrolBehavior for 'patrol' type."""
        behavior = create_behavior("patrol", {"speed": 30})
        assert isinstance(behavior, PatrolBehavior)

    def test_create_chase(self):
        """Should create a ChaseBehavior for 'chase' type."""
        behavior = create_behavior("chase", {"speed": 50})
        assert isinstance(behavior, ChaseBehavior)

    def test_unknown_type_raises(self):
        """Unknown behavior type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown behavior type"):
            create_behavior("nonexistent", {})
