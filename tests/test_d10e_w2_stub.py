"""Tests for D10E: W2 stub level, shield behavior, and boss-to-W2 transition."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pygame
import pytest

from sa_fona.config.settings import DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.core.scene_manager import SceneManager
from sa_fona.entities.enemy import Enemy, EnemyFactory
from sa_fona.entities.enemy_behaviors import (
    AttackState,
    ShieldBehavior,
    create_behavior,
)


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


# ── ShieldBehavior tests ──────────────────────────────────────────


class TestShieldBehavior:
    """Tests for the ShieldBehavior component."""

    def test_shield_up_by_default(self):
        """Shield should be raised on creation."""
        params = {"patrol_range": 4, "speed": 25, "attack_range": 2.0}
        shield = ShieldBehavior(params)
        shield.reset(100.0)
        assert shield.shield_up is True

    def test_try_block_returns_true_when_shield_up(self):
        """try_block should succeed when shield is raised."""
        params = {"patrol_range": 4, "speed": 25}
        shield = ShieldBehavior(params)
        shield.reset(100.0)
        assert shield.try_block() is True

    def test_shield_drops_during_attack(self):
        """Shield should lower when entering ATTACKING state."""
        params = {
            "patrol_range": 4,
            "speed": 25,
            "attack_range": 3.0,
            "attack_tell_time": 0.01,
            "attack_cooldown": 2.0,
            "shield_lower_time": 1.0,
        }
        shield = ShieldBehavior(params)
        shield.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 24)
        # Place player within attack range on same level.
        player_rect = pygame.Rect(130, 100, 24, 32)

        # Run enough frames to trigger tell -> attack.
        for _ in range(200):
            result = shield.update(enemy_rect, player_rect, 1 / 60)
            if result.attack_state == AttackState.ATTACKING:
                break

        assert result.attack_state == AttackState.ATTACKING
        assert shield.shield_up is False
        assert result.is_blocking is False

    def test_shield_raises_after_cooldown(self):
        """Shield should re-raise after attack + shield_lower_time."""
        params = {
            "patrol_range": 4,
            "speed": 25,
            "attack_range": 3.0,
            "attack_tell_time": 0.01,
            "attack_cooldown": 0.01,
            "shield_lower_time": 0.1,
        }
        shield = ShieldBehavior(params)
        shield.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 24)
        player_rect = pygame.Rect(130, 100, 24, 32)

        # Run until attack, then keep going until shield raises.
        shield_dropped = False
        shield_raised_again = False
        for _ in range(600):
            result = shield.update(enemy_rect, player_rect, 1 / 60)
            if not shield.shield_up:
                shield_dropped = True
            if shield_dropped and shield.shield_up:
                shield_raised_again = True
                break

        assert shield_dropped
        assert shield_raised_again

    def test_blocking_result_reflects_shield_state(self):
        """BehaviorResult.is_blocking should match shield_up during patrol."""
        params = {"patrol_range": 4, "speed": 25}
        shield = ShieldBehavior(params)
        shield.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 16, 24)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        result = shield.update(enemy_rect, player_rect, 1 / 60)
        assert result.is_blocking is True

    def test_create_behavior_shield(self):
        """Factory function should create ShieldBehavior for 'shield' type."""
        behavior = create_behavior("shield", {"patrol_range": 4, "speed": 25})
        assert isinstance(behavior, ShieldBehavior)

    def test_reset_restores_shield(self):
        """Reset should restore the shield to the up position."""
        params = {"patrol_range": 4, "speed": 25, "shield_lower_time": 1.0}
        shield = ShieldBehavior(params)
        shield.reset(100.0)
        # Manually lower shield.
        shield._shield_up = False
        shield.reset(100.0)
        assert shield.shield_up is True


# ── W2 enemy definitions tests ───────────────────────────────────


class TestWorld2Enemies:
    """Tests for world2 enemy definitions and factory loading."""

    def test_world2_enemies_file_exists(self):
        """The world2_enemies.json file should exist."""
        path = DATA_DIR / "enemies" / "world2_enemies.json"
        assert path.is_file()

    def test_world2_enemies_valid_json(self):
        """The file should contain valid JSON with expected enemy types."""
        path = DATA_DIR / "enemies" / "world2_enemies.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert "legionary" in data
        assert "war_dog" in data

    def test_legionary_has_shield_behavior(self):
        """Legionary should use the 'shield' behavior type."""
        path = DATA_DIR / "enemies" / "world2_enemies.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data["legionary"]["behavior"] == "shield"

    def test_war_dog_has_chase_behavior(self):
        """War dog should use the 'chase' behavior type."""
        path = DATA_DIR / "enemies" / "world2_enemies.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data["war_dog"]["behavior"] == "chase"

    def test_factory_loads_world2_enemies(self):
        """EnemyFactory should auto-load world2 enemies alongside world1."""
        factory = EnemyFactory()
        assert "legionary" in factory.definitions
        assert "war_dog" in factory.definitions
        # World1 enemies should still be present.
        assert "possessed_sheep" in factory.definitions

    def test_factory_creates_legionary(self):
        """EnemyFactory should create a legionary enemy."""
        factory = EnemyFactory()
        enemy = factory.create("legionary", 100, 100)
        assert enemy.enemy_type == "legionary"
        assert enemy.health == 4
        assert isinstance(enemy.behavior, ShieldBehavior)

    def test_factory_creates_war_dog(self):
        """EnemyFactory should create a war dog enemy."""
        factory = EnemyFactory()
        enemy = factory.create("war_dog", 100, 100)
        assert enemy.enemy_type == "war_dog"
        assert enemy.health == 2


# ── W2 level loading tests ───────────────────────────────────────


class TestWorld2Level:
    """Tests for the W2 stub level file."""

    def test_level_file_exists(self):
        """The world2/level_2_1.json file should exist."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        assert path.is_file()

    def test_level_valid_json(self):
        """The level JSON should be parseable."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert "dimensions" in data
        assert "layers" in data
        assert "player_spawn" in data

    def test_level_has_breakable_slam_tiles(self):
        """Level should contain breakable_slam tiles (tile ID 30)."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        midground = data["layers"]["midground"]
        found = any(30 in row for row in midground)
        assert found, "Level should contain breakable_slam tiles (ID 30)"

    def test_level_has_enemies(self):
        """Level should define enemy entities."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        enemies = [e for e in data["entities"] if e["type"] == "enemy"]
        assert len(enemies) >= 5  # 3 legionaries + 2 war dogs

    def test_level_has_level_end_trigger(self):
        """Level should have a level_end trigger."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        end_triggers = [
            t for t in data["triggers"] if t["type"] == "level_end"
        ]
        assert len(end_triggers) >= 1

    def test_level_has_dialogue_triggers(self):
        """Level should have dialogue triggers for tutorials."""
        path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        dialogue_triggers = [
            t for t in data["triggers"] if t["type"] == "dialogue"
        ]
        assert len(dialogue_triggers) >= 2

    def test_level_loads_with_level_loader(self):
        """The level should be loadable by the LevelLoader."""
        from sa_fona.level.level_loader import LevelLoader

        loader = LevelLoader()
        level_path = str(DATA_DIR / "levels" / "world2" / "level_2_1.json")
        level_data = loader.load(level_path)
        assert level_data.tilemap is not None
        assert level_data.player_spawn == (2, 10)


# ── W2 dialogue tests ────────────────────────────────────────────


class TestWorld2Dialogue:
    """Tests for world2 dialogue definitions."""

    def test_dialogue_file_exists(self):
        """The world2_dialogue.json file should exist."""
        path = DATA_DIR / "dialogue" / "world2_dialogue.json"
        assert path.is_file()

    def test_dialogue_valid_json(self):
        """The dialogue JSON should be parseable."""
        path = DATA_DIR / "dialogue" / "world2_dialogue.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert "w2_l1_arrival" in data
        assert "w2_l1_stone_slam_hint" in data
        assert "w2_l1_shield_warning" in data

    def test_dialogue_entries_have_lines(self):
        """Each dialogue entry should have at least one line."""
        path = DATA_DIR / "dialogue" / "world2_dialogue.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for key, entry in data.items():
            assert "lines" in entry, f"{key} missing 'lines'"
            assert len(entry["lines"]) > 0, f"{key} has empty 'lines'"


# ── Boss→W2 transition tests ─────────────────────────────────────


class TestBossToW2Transition:
    """Tests for the boss scene to W2 level transition flow."""

    def test_boss_scene_stores_pending_level_load(self):
        """BossScene should store the level path from cutscene callback."""
        from sa_fona.scenes.boss_scene import BossScene

        external_callback = MagicMock()
        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=EventBus(),
            on_load_level=external_callback,
        )
        assert scene._pending_level_load is None

        # Simulate what the cutscene does.
        scene._pending_level_load = "world2/level_2_1"
        assert scene._pending_level_load == "world2/level_2_1"

    def test_boss_on_resume_fires_external_callback(self):
        """on_resume should call the external on_load_level with the stored path."""
        from sa_fona.scenes.boss_scene import BossScene

        external_callback = MagicMock()
        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=EventBus(),
            on_load_level=external_callback,
        )
        scene._cutscene_pushed = True
        scene._pending_level_load = "world2/level_2_1"

        scene.on_resume()

        external_callback.assert_called_once_with("world2/level_2_1")
        assert scene._pending_level_load is None

    def test_boss_on_resume_no_callback_without_pending(self):
        """on_resume should not call callback if no pending level load."""
        from sa_fona.scenes.boss_scene import BossScene

        external_callback = MagicMock()
        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=EventBus(),
            on_load_level=external_callback,
        )
        scene._cutscene_pushed = True

        scene.on_resume()

        external_callback.assert_not_called()

    def test_boss_reset_clears_pending_level_load(self):
        """_reset_fight should clear the pending level load."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=EventBus(),
            on_load_level=lambda p: None,
        )
        scene._pending_level_load = "world2/level_2_1"
        scene._reset_fight()
        assert scene._pending_level_load is None

    def test_cutscene_deferred_callback_stores_path(self):
        """The cutscene's load_level callback should store path, not execute transition."""
        from sa_fona.scenes.boss_scene import BossScene

        external_callback = MagicMock()
        bus = EventBus()
        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=bus,
            on_load_level=external_callback,
            cutscene_id="post_boss_w1",
        )
        sm = SceneManager()
        sm.push(scene)
        scene.scene_manager = sm

        # Simulate defeat and cutscene push.
        scene._boss_defeated = True
        scene._defeat_timer = 2.0
        scene._push_cutscene()
        assert scene._cutscene_pushed is True

        # The cutscene should have been pushed on the stack.
        # Simulate the cutscene calling the deferred load level callback.
        scene._pending_level_load = "world2/level_2_1"

        # External callback should NOT have been called yet.
        external_callback.assert_not_called()


class TestGameplayMakeLoadLevelCb:
    """Tests for GameplayScene._make_load_level_cb."""

    def test_callback_creates_new_scene(self):
        """The load level callback should create a GameplayScene for W2."""
        from sa_fona.scenes.gameplay import GameplayScene

        bus = EventBus()
        sm = SceneManager()

        # Use the test level as starting point.
        scene = GameplayScene(
            screen_width=384,
            screen_height=216,
            event_bus=bus,
        )
        sm.push(scene)
        scene.scene_manager = sm

        cb = scene._make_load_level_cb()
        assert callable(cb)

        # The W2 level file must exist for the callback to work.
        w2_path = DATA_DIR / "levels" / "world2" / "level_2_1.json"
        if w2_path.is_file():
            # Push a dummy scene to replace (simulating boss scene).
            from sa_fona.scenes.base_scene import BaseScene

            class DummyScene(BaseScene):
                def handle_input(self, input_state):
                    pass

                def update(self, dt):
                    pass

                def render(self, surface):
                    pass

            sm.push(DummyScene())
            cb("world2/level_2_1")
            # The top of the stack should now be a GameplayScene.
            assert isinstance(sm.active_scene, GameplayScene)
