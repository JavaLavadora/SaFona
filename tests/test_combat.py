"""Tests for the CombatSystem: damage dealing, invincibility frames, and death."""

from __future__ import annotations

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.entities.enemy import Enemy, EnemyFactory
from sa_fona.entities.player import Player
from sa_fona.entities.projectile import Projectile, ProjectileType
from sa_fona.systems.combat import CombatSystem, PLAYER_INVINCIBILITY_DURATION
from sa_fona.systems.sling_system import MeleeHitbox


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield
    # No quit -- shared across tests in session.


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def combat(event_bus):
    cs = CombatSystem(event_bus)
    cs.set_player_health(3.0, 3)
    return cs


@pytest.fixture
def player():
    return Player(100, 100)


@pytest.fixture
def sheep_def():
    return {
        "display_name": "Test Sheep",
        "health": 2,
        "contact_damage": 0.5,
        "behavior": "patrol",
        "behavior_params": {"patrol_range": 5, "speed": 40},
        "hitbox": {"w": 16, "h": 16},
        "drops": {"stones": {"min": 1, "max": 2}, "heart_chance": 0.0},
    }


def _make_projectile(x, y, direction=1.0, damage=1.0):
    """Helper to create a test projectile."""
    return Projectile(
        x=x, y=y, width=8, height=8,
        direction=direction, speed=250.0,
        damage=damage, charge_tier=1,
        max_range=200.0,
        projectile_type=ProjectileType.BASIC_STONE,
    )


class TestCombatDamageDealing:
    """Test that the combat system correctly resolves damage."""

    def test_projectile_damages_enemy(self, combat, player, event_bus, sheep_def):
        """A projectile overlapping an enemy should deal damage."""
        enemy = Enemy(100, 100, "possessed_sheep", sheep_def)
        proj = _make_projectile(100, 100, damage=1.0)

        drops = combat.update(player, [enemy], [proj], [], 1 / 60)

        assert enemy.health == 1.0
        assert not proj.active  # Projectile destroyed on hit.

    def test_melee_damages_enemy(self, combat, player, event_bus, sheep_def):
        """A melee hitbox overlapping an enemy should deal damage."""
        enemy = Enemy(100, 100, "possessed_sheep", sheep_def)
        hitbox = MeleeHitbox(
            rect=pygame.Rect(100, 100, 28, 20),
            damage=1.0,
            timer=0.1,
        )

        combat.update(player, [enemy], [], [hitbox], 1 / 60)

        assert enemy.health == 1.0

    def test_enemy_contact_damages_player(self, combat, player, event_bus, sheep_def):
        """Player touching an enemy should take contact damage."""
        # Place enemy right on top of the player.
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)

        assert combat.player_hearts == 2.5  # 3.0 - 0.5 contact damage.

    def test_killing_enemy_publishes_event(self, combat, player, event_bus, sheep_def):
        """Killing an enemy should publish enemy_killed event."""
        events = []
        event_bus.subscribe("enemy_killed", lambda **kw: events.append(kw))

        # Enemy with 1 HP, hit by 1 damage projectile.
        sheep_def_1hp = dict(sheep_def)
        sheep_def_1hp["health"] = 1
        enemy = Enemy(100, 100, "possessed_sheep", sheep_def_1hp)
        proj = _make_projectile(100, 100, damage=1.0)

        combat.update(player, [enemy], [proj], [], 1 / 60)

        assert not enemy.is_alive
        assert len(events) == 1
        assert events[0]["enemy_type"] == "possessed_sheep"

    def test_killing_enemy_drops_pickups(self, combat, player, event_bus, sheep_def):
        """Killing an enemy should produce pickup drops."""
        sheep_def_1hp = dict(sheep_def)
        sheep_def_1hp["health"] = 1
        sheep_def_1hp["drops"] = {
            "stones": {"min": 2, "max": 2},
            "heart_chance": 0.0,
        }
        enemy = Enemy(100, 100, "possessed_sheep", sheep_def_1hp)
        proj = _make_projectile(100, 100, damage=1.0)

        drops = combat.update(player, [enemy], [proj], [], 1 / 60)

        assert len(drops) == 2  # 2 stone pickups, 0 hearts.


class TestInvincibilityFrames:
    """Test player invincibility after taking damage."""

    def test_player_becomes_invincible_after_damage(
        self, combat, player, event_bus, sheep_def
    ):
        """Player should be invincible after taking damage."""
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)

        assert combat.player_invincible

    def test_no_double_damage_during_invincibility(
        self, combat, player, event_bus, sheep_def
    ):
        """Player should not take damage during invincibility."""
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        # First hit.
        combat.update(player, [enemy], [], [], 1 / 60)
        health_after_first = combat.player_hearts

        # Second frame -- still overlapping, but invincible.
        combat.update(player, [enemy], [], [], 1 / 60)

        assert combat.player_hearts == health_after_first

    def test_invincibility_wears_off(self, combat, player, event_bus, sheep_def):
        """Invincibility should expire after the duration."""
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)
        assert combat.player_invincible

        # Advance past invincibility duration.
        for _ in range(100):
            combat.update(player, [], [], [], 1 / 60)

        assert not combat.player_invincible

    def test_player_blink_toggles_visibility(
        self, combat, player, event_bus, sheep_def
    ):
        """Player visibility should toggle during invincibility (blink)."""
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)

        # Collect visibility values over several frames.
        visibility_states = []
        for _ in range(20):
            combat.update(player, [], [], [], 0.02)
            visibility_states.append(combat.player_visible)

        # Should have both True and False values (blinking).
        assert True in visibility_states
        assert False in visibility_states


class TestPlayerDeath:
    """Test player death and game over triggering."""

    def test_player_dies_at_zero_hearts(self, combat, player, event_bus, sheep_def):
        """Player should die when hearts reach 0."""
        died_events = []
        event_bus.subscribe("player_died", lambda **kw: died_events.append(True))

        # Set health to exactly 0.5 (one more hit from sheep kills).
        combat.set_player_health(0.5, 3)

        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)

        assert combat.player_dead
        assert len(died_events) == 1

    def test_combat_stops_after_death(self, combat, player, event_bus, sheep_def):
        """No further combat should happen after the player dies."""
        combat.set_player_health(0.5, 3)
        enemy = Enemy(
            player.rect.x, player.rect.y,
            "possessed_sheep", sheep_def,
        )

        combat.update(player, [enemy], [], [], 1 / 60)
        assert combat.player_dead

        # Further updates should return empty.
        result = combat.update(player, [enemy], [], [], 1 / 60)
        assert result == []

    def test_heart_collection_tracked(self, combat, event_bus):
        """Combat system should track heart collection for accurate health."""
        combat.set_player_health(2.0, 3)
        event_bus.publish("heart_collected", amount=1.0)

        assert combat.player_hearts == 3.0

    def test_heart_collection_capped_at_max(self, combat, event_bus):
        """Heart collection should not exceed max hearts."""
        combat.set_player_health(3.0, 3)
        event_bus.publish("heart_collected", amount=1.0)

        assert combat.player_hearts == 3.0
