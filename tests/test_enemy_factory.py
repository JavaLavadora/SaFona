"""Tests for the EnemyFactory: JSON loading and enemy creation."""

from __future__ import annotations

import json
import os
import tempfile

import pygame
import pytest

from sa_fona.entities.enemy import Enemy, EnemyFactory
from sa_fona.entities.enemy_behaviors import PatrolBehavior, ChaseBehavior
from sa_fona.level.tilemap import TILE_SIZE


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


@pytest.fixture
def definitions():
    """Sample enemy definitions dict."""
    return {
        "test_sheep": {
            "display_name": "Test Sheep",
            "health": 2,
            "contact_damage": 0.5,
            "behavior": "patrol",
            "behavior_params": {"patrol_range": 5, "speed": 40},
            "hitbox": {"w": 16, "h": 16},
            "drops": {"stones": {"min": 1, "max": 2}, "heart_chance": 0.1},
        },
        "test_warrior": {
            "display_name": "Test Warrior",
            "health": 3,
            "contact_damage": 1.0,
            "behavior": "chase",
            "behavior_params": {"chase_range": 6, "speed": 50},
            "hitbox": {"w": 16, "h": 24},
            "drops": {"stones": {"min": 1, "max": 3}, "heart_chance": 0.15},
        },
    }


@pytest.fixture
def factory_path(definitions):
    """Create a temporary JSON file with enemy definitions."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(definitions, f)
        path = f.name

    yield path
    os.unlink(path)


class TestEnemyFactory:
    """Tests for creating enemies from JSON definitions."""

    def test_load_definitions(self, factory_path):
        """Factory should load definitions from JSON."""
        factory = EnemyFactory(factory_path)
        assert "test_sheep" in factory.definitions
        assert "test_warrior" in factory.definitions

    def test_create_sheep(self, factory_path):
        """Factory should create a sheep enemy with correct stats."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_sheep", 100, 200)

        assert isinstance(enemy, Enemy)
        assert enemy.enemy_type == "test_sheep"
        assert enemy.health == 2
        assert enemy.contact_damage == 0.5
        shrink = Enemy._HITBOX_SHRINK
        assert enemy.rect.x == 100 + shrink
        assert enemy.rect.y == 200 + shrink
        assert enemy.rect.width == 16 - shrink * 2
        assert enemy.rect.height == 16 - shrink * 2
        assert isinstance(enemy.behavior, PatrolBehavior)

    def test_create_warrior(self, factory_path):
        """Factory should create a warrior enemy with chase behavior."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_warrior", 200, 150)

        assert enemy.enemy_type == "test_warrior"
        assert enemy.health == 3
        assert enemy.contact_damage == 1.0
        shrink = Enemy._HITBOX_SHRINK
        assert enemy.rect.width == 16 - shrink * 2
        assert enemy.rect.height == 24 - shrink * 2
        assert isinstance(enemy.behavior, ChaseBehavior)

    def test_create_unknown_type_raises(self, factory_path):
        """Creating an unknown enemy type should raise ValueError."""
        factory = EnemyFactory(factory_path)
        with pytest.raises(ValueError, match="Unknown enemy type"):
            factory.create("nonexistent", 0, 0)

    def test_create_from_entity_def(self, factory_path):
        """Factory should create enemies from level entity definitions."""
        factory = EnemyFactory(factory_path)
        ent_def = {"type": "enemy", "enemy_type": "test_sheep", "x": 10, "y": 5}
        enemy = factory.create_from_entity_def(ent_def)

        assert enemy.enemy_type == "test_sheep"
        shrink = Enemy._HITBOX_SHRINK
        assert enemy.rect.x == 10 * TILE_SIZE + shrink
        assert enemy.rect.y == 5 * TILE_SIZE + shrink

    def test_missing_file_creates_empty_factory(self):
        """Factory with missing file should have no definitions."""
        factory = EnemyFactory("/nonexistent/path.json")
        assert len(factory.definitions) == 0

    def test_default_path_loads_world1(self):
        """Factory with default path should load world1_enemies.json."""
        factory = EnemyFactory()
        # Should have the three W1 types.
        assert "possessed_sheep" in factory.definitions
        assert "rival_warrior" in factory.definitions
        assert "stone_guardian" in factory.definitions


class TestEnemyEntity:
    """Tests for the Enemy entity directly."""

    def test_take_damage(self, factory_path):
        """Enemy should lose health when damaged."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_sheep", 0, 0)

        applied = enemy.take_damage(1.0)
        assert applied
        assert enemy.health == 1.0

    def test_invincibility_prevents_double_damage(self, factory_path):
        """Enemy should not take damage during invincibility frames."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_sheep", 0, 0)

        enemy.take_damage(1.0)
        # Immediately try to damage again -- should be blocked.
        applied = enemy.take_damage(1.0)
        assert not applied
        assert enemy.health == 1.0

    def test_death_on_zero_health(self, factory_path):
        """Enemy should die when health reaches 0."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_sheep", 0, 0)

        enemy.take_damage(2.0)
        assert not enemy.is_alive
        assert not enemy.active

    def test_get_drops(self, factory_path):
        """Dead enemy should produce pickup drops."""
        factory = EnemyFactory(factory_path)
        enemy = factory.create("test_sheep", 100, 100)

        enemy.take_damage(2.0)
        drops = enemy.get_drops()

        # Should have at least 1 stone pickup (min drops = 1).
        assert len(drops) >= 1
