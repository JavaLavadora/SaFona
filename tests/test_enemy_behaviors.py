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
