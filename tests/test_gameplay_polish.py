"""Tests for gameplay polish fixes: wall-facing, respawn health, dialogue suppression.

These tests verify:
1. Enemies near walls face away from the wall on spawn.
2. Player respawns with at least half max health after dying.
3. Dialogue triggers don't re-fire after a same-level respawn.
"""

from __future__ import annotations

import pygame
import pytest

from sa_fona.entities.enemy import Enemy, EnemyFactory
from sa_fona.entities.enemy_behaviors import PatrolBehavior, GuardianBehavior
from sa_fona.level.tilemap import TileMap, TILE_SIZE
from sa_fona.level.trigger import Trigger, TriggerSystem, TriggerType
from sa_fona.core.event_bus import EventBus


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


# ── Fix 1: Enemy wall-facing on spawn ────────────────────────────


class TestEnemyWallFacing:
    """Enemies near a wall should face away from it on spawn."""

    def _make_tilemap_with_right_wall(self):
        """Create a tilemap with a wall on the right side.

        Layout (6 wide, 4 tall):
            Row 0: empty
            Row 1: empty  empty  empty  empty  WALL  WALL
            Row 2: empty  empty  empty  empty  WALL  WALL  <- enemy level
            Row 3: solid  solid  solid  solid  solid solid  <- ground
        """
        tile_data = {
            "dimensions": {"width": 6, "height": 4},
            "layers": {
                "midground": [
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 1, 1],
                    [0, 0, 0, 0, 1, 1],
                    [1, 1, 1, 1, 1, 1],
                ],
            },
            "collision_types": {"solid": [1]},
        }
        return TileMap(tile_data)

    def _make_tilemap_with_left_wall(self):
        """Create a tilemap with a wall on the left side.

        Layout (6 wide, 4 tall):
            Row 0: empty
            Row 1: WALL  WALL  empty  empty  empty  empty
            Row 2: WALL  WALL  empty  empty  empty  empty  <- enemy level
            Row 3: solid  solid  solid  solid  solid solid  <- ground
        """
        tile_data = {
            "dimensions": {"width": 6, "height": 4},
            "layers": {
                "midground": [
                    [0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1],
                ],
            },
            "collision_types": {"solid": [1]},
        }
        return TileMap(tile_data)

    def _make_tilemap_open(self):
        """Create a tilemap with no walls near the enemy.

        Layout (6 wide, 4 tall):
            Row 0-2: all empty
            Row 3: all solid
        """
        tile_data = {
            "dimensions": {"width": 6, "height": 4},
            "layers": {
                "midground": [
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1],
                ],
            },
            "collision_types": {"solid": [1]},
        }
        return TileMap(tile_data)

    def _make_enemy(self, x: float, y: float) -> Enemy:
        """Create a basic enemy with patrol behavior."""
        definition = {
            "health": 2,
            "contact_damage": 0.5,
            "hitbox": {"w": 16, "h": 16},
            "behavior": "patrol",
            "behavior_params": {"patrol_range": 5, "speed": 40},
        }
        return Enemy(x, y, "possessed_sheep", definition)

    def test_faces_left_when_wall_on_right(self):
        """Enemy near a right wall should face left."""
        tilemap = self._make_tilemap_with_right_wall()
        # Place enemy at column 3, row 2 (just left of the wall at col 4).
        enemy = self._make_enemy(3 * TILE_SIZE, 2 * TILE_SIZE)
        enemy.adjust_facing_for_walls(tilemap)

        assert not enemy.facing_right

    def test_faces_right_when_wall_on_left(self):
        """Enemy near a left wall should face right."""
        tilemap = self._make_tilemap_with_left_wall()
        # Place enemy at column 2, row 2 (just right of the wall at col 1).
        enemy = self._make_enemy(2 * TILE_SIZE, 2 * TILE_SIZE)
        enemy.adjust_facing_for_walls(tilemap)

        assert enemy.facing_right

    def test_no_change_when_no_walls(self):
        """Enemy in open space should keep default facing (right)."""
        tilemap = self._make_tilemap_open()
        enemy = self._make_enemy(3 * TILE_SIZE, 2 * TILE_SIZE)
        enemy.adjust_facing_for_walls(tilemap)

        # Default is facing right, should remain unchanged.
        assert enemy.facing_right

    def test_behavior_direction_matches_facing(self):
        """Behavior patrol direction should match the adjusted facing."""
        tilemap = self._make_tilemap_with_right_wall()
        enemy = self._make_enemy(3 * TILE_SIZE, 2 * TILE_SIZE)
        enemy.adjust_facing_for_walls(tilemap)

        assert not enemy.facing_right
        assert enemy.behavior._direction == -1.0


class TestSetInitialDirection:
    """Tests for the set_initial_direction behavior method."""

    def test_patrol_set_initial_direction(self):
        """PatrolBehavior should update _direction."""
        params = {"patrol_range": 5, "speed": 40}
        patrol = PatrolBehavior(params)
        patrol.reset(100.0)
        assert patrol._direction == 1.0  # default

        patrol.set_initial_direction(-1.0)
        assert patrol._direction == -1.0

    def test_guardian_set_initial_direction(self):
        """GuardianBehavior should update _direction."""
        params = {"patrol_range": 3, "speed": 20}
        guardian = GuardianBehavior(params)
        guardian.reset(100.0)
        assert guardian._direction == 1.0

        guardian.set_initial_direction(-1.0)
        assert guardian._direction == -1.0


# ── Fix 2: Respawn with at least half health ─────────────────────


class TestRespawnHealth:
    """Player should respawn with at least half max health."""

    def test_reset_level_restores_at_least_half_health(self):
        """After death-respawn, health should be >= max_health / 2."""
        from sa_fona.config.settings import BASE_WIDTH, BASE_HEIGHT
        from sa_fona.scenes.gameplay import GameplayScene

        bus = EventBus()
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)

        # Simulate a save system with a snapshot that has low health.
        class FakeSave:
            def __init__(self):
                self.level_entry_snapshot = {
                    "max_hearts": 4,
                    "current_hearts": 1.0,
                    "stone_count": 5,
                }
                self.state = {}

            def set_level(self, path):
                pass

            def snapshot_level_entry(self, **kwargs):
                pass

            def rollback_to_snapshot(self):
                return self.level_entry_snapshot

            def save(self):
                pass

            def set_player_state(self, **kwargs):
                pass

        scene.save_system = FakeSave()
        scene._reset_level()

        # Health should be at least half of max (4 / 2 = 2.0).
        assert scene.combat.player_hearts >= 2.0

    def test_reset_level_keeps_higher_health(self):
        """If snapshot health is already above half, it should be preserved."""
        from sa_fona.config.settings import BASE_WIDTH, BASE_HEIGHT
        from sa_fona.scenes.gameplay import GameplayScene

        bus = EventBus()
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)

        class FakeSave:
            def __init__(self):
                self.level_entry_snapshot = {
                    "max_hearts": 4,
                    "current_hearts": 3.0,
                    "stone_count": 5,
                }
                self.state = {}

            def set_level(self, path):
                pass

            def snapshot_level_entry(self, **kwargs):
                pass

            def rollback_to_snapshot(self):
                return self.level_entry_snapshot

            def save(self):
                pass

            def set_player_state(self, **kwargs):
                pass

        scene.save_system = FakeSave()
        scene._reset_level()

        # Health should be 3.0 (higher than half of 4 = 2.0).
        assert scene.combat.player_hearts == 3.0


# ── Fix 3: Dialogue triggers suppressed after respawn ────────────


class TestDialogueSuppression:
    """Dialogue triggers should not re-fire after same-level respawn."""

    def test_get_fired_dialogue_ids_empty_initially(self):
        """No dialogues should be reported as fired initially."""
        bus = EventBus()
        ts = TriggerSystem(bus)

        trigger = Trigger(
            rect=pygame.Rect(0, 0, 16, 16),
            trigger_type=TriggerType.DIALOGUE,
            once=True,
            properties={"dialogue_id": "intro"},
        )
        ts.add(trigger)

        assert ts.get_fired_dialogue_ids() == set()

    def test_get_fired_dialogue_ids_after_fire(self):
        """Fired dialogue triggers should appear in the returned set."""
        bus = EventBus()
        ts = TriggerSystem(bus)

        trigger = Trigger(
            rect=pygame.Rect(0, 0, 16, 16),
            trigger_type=TriggerType.DIALOGUE,
            once=True,
            properties={"dialogue_id": "intro"},
        )
        ts.add(trigger)

        # Fire the trigger.
        trigger.fire(bus)
        assert not trigger.active

        fired = ts.get_fired_dialogue_ids()
        assert "intro" in fired

    def test_suppress_dialogue_ids(self):
        """Suppressed dialogue triggers should be deactivated."""
        bus = EventBus()
        ts = TriggerSystem(bus)

        trigger = Trigger(
            rect=pygame.Rect(0, 0, 16, 16),
            trigger_type=TriggerType.DIALOGUE,
            once=True,
            properties={"dialogue_id": "intro"},
        )
        ts.add(trigger)
        assert trigger.active

        ts.suppress_dialogue_ids({"intro"})
        assert not trigger.active

    def test_suppress_leaves_other_triggers(self):
        """Non-dialogue triggers should not be affected by suppression."""
        bus = EventBus()
        ts = TriggerSystem(bus)

        dialogue = Trigger(
            rect=pygame.Rect(0, 0, 16, 16),
            trigger_type=TriggerType.DIALOGUE,
            once=True,
            properties={"dialogue_id": "intro"},
        )
        save_point = Trigger(
            rect=pygame.Rect(32, 0, 16, 16),
            trigger_type=TriggerType.SAVE_POINT,
            once=True,
            properties={},
        )
        ts.add(dialogue)
        ts.add(save_point)

        ts.suppress_dialogue_ids({"intro"})

        assert not dialogue.active
        assert save_point.active  # Should NOT be affected.

    def test_suppress_does_not_affect_non_once_triggers(self):
        """Non-once dialogue triggers should not be suppressed."""
        bus = EventBus()
        ts = TriggerSystem(bus)

        trigger = Trigger(
            rect=pygame.Rect(0, 0, 16, 16),
            trigger_type=TriggerType.DIALOGUE,
            once=False,
            properties={"dialogue_id": "intro"},
        )
        ts.add(trigger)

        ts.suppress_dialogue_ids({"intro"})
        assert trigger.active  # once=False should not be suppressed.

    def test_reset_level_preserves_dialogue_state(self):
        """After _reset_level, already-fired dialogues should stay suppressed."""
        from sa_fona.config.settings import BASE_WIDTH, BASE_HEIGHT
        from sa_fona.scenes.gameplay import GameplayScene

        bus = EventBus()
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)

        # Find dialogue triggers and fire them.
        dialogue_triggers = [
            t for t in scene.trigger_system.triggers
            if t.trigger_type == TriggerType.DIALOGUE
        ]
        for t in dialogue_triggers:
            t.fire(bus)

        fired_ids = scene.trigger_system.get_fired_dialogue_ids()

        # Reset (simulates same-level respawn).
        scene._reset_level()

        # Check that all previously-fired dialogue triggers are inactive.
        for t in scene.trigger_system.triggers:
            if t.trigger_type == TriggerType.DIALOGUE and t.once:
                dialogue_id = t.properties.get("dialogue_id", "")
                if dialogue_id in fired_ids:
                    assert not t.active, (
                        f"Dialogue '{dialogue_id}' should be suppressed after respawn"
                    )
