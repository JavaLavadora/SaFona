"""Tests for BossEntity, BouDePedra, BossHealthBar, and BossScene.

Covers:
- BossEntity phase transitions (HP thresholds)
- Attack pattern timing (tell durations, punish windows)
- Damage during punish windows vs. invulnerable states
- Phase 3 exposed core damage multipliers
- Boss health bar rendering data
- BossScene integration
"""

from __future__ import annotations

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.entities.boss_entity import BossEntity, BossState
from sa_fona.entities.bosses.bou_de_pedra import (
    BossProjectile,
    BouDePedra,
    DestructiblePillar,
    ShadowMarker,
)
from sa_fona.ui.boss_health_bar import BossHealthBar


# ── Fixtures ──────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _init_pygame():
    """Initialize pygame for test surfaces and fonts."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def event_bus() -> EventBus:
    """Create a fresh event bus for each test."""
    return EventBus()


@pytest.fixture
def boss_definition() -> dict:
    """Minimal boss definition matching the JSON structure."""
    return {
        "boss_id": "bou_de_pedra",
        "display_name": "Es Bou de Pedra",
        "world": 1,
        "health": 30,
        "contact_damage": 1.0,
        "hitbox": {"w": 56, "h": 48},
        "arena": {
            "width": 25,
            "height": 14,
            "destructible_pillars": 4,
            "pillar_positions": [
                {"x": 5, "y": 10},
                {"x": 10, "y": 10},
                {"x": 15, "y": 10},
                {"x": 20, "y": 10},
            ],
            "player_spawn": {"x": 2, "y": 11},
            "boss_spawn": {"x": 20, "y": 9},
        },
        "phases": [
            {
                "phase": 1,
                "name": "The Charge",
                "hp_range": [0.66, 1.0],
                "color": [140, 140, 140],
                "patterns": [
                    {
                        "id": "bull_rush",
                        "tell_time": 1.0,
                        "damage": 1.5,
                        "punish_window": 2.5,
                        "weight": 0.6,
                        "params": {
                            "speed": 200,
                            "stun_on_wall_hit": True,
                            "destroys_pillars": True,
                        },
                    },
                    {
                        "id": "headbutt",
                        "tell_time": 0.5,
                        "damage": 1.0,
                        "punish_window": 1.5,
                        "weight": 0.4,
                        "params": {"range": 2.0},
                    },
                ],
                "transition_effect": "roar_screen_shake",
            },
            {
                "phase": 2,
                "name": "The Stomp",
                "hp_range": [0.33, 0.66],
                "color": [220, 140, 40],
                "patterns": [
                    {
                        "id": "bull_rush",
                        "tell_time": 0.8,
                        "damage": 1.5,
                        "punish_window": 2.5,
                        "weight": 0.35,
                        "params": {"speed": 250},
                    },
                    {
                        "id": "ground_stomp",
                        "tell_time": 1.2,
                        "damage": 1.0,
                        "punish_window": 2.0,
                        "weight": 0.35,
                        "params": {"shockwave_range": 6, "direct_damage": 1.5},
                    },
                    {
                        "id": "rock_hurl",
                        "tell_time": 0.8,
                        "damage": 1.0,
                        "punish_window": 1.5,
                        "weight": 0.3,
                        "params": {"rock_count": 3},
                    },
                ],
                "transition_effect": "core_reveal",
            },
            {
                "phase": 3,
                "name": "The Core",
                "hp_range": [0.0, 0.33],
                "color": [220, 40, 40],
                "patterns": [
                    {
                        "id": "frenzy_rush",
                        "tell_time": 0.6,
                        "damage": 1.5,
                        "punish_window": 2.5,
                        "weight": 0.5,
                        "params": {"speed": 280, "bounces": 3},
                    },
                    {
                        "id": "core_pulse",
                        "tell_time": 1.0,
                        "damage": 1.0,
                        "punish_window": 2.0,
                        "weight": 0.5,
                        "params": {"radius": 8},
                    },
                ],
                "weak_point": {
                    "location": "chest",
                    "charge_multiplier": 2.0,
                    "tier3_multiplier": 3.0,
                },
            },
        ],
        "post_defeat": {
            "mask_granted": "stone_slam",
            "dialogue_id": "dimoni_sant_joan_grant",
            "cutscene": "w1_post_boss",
        },
    }


@pytest.fixture
def boss(boss_definition, event_bus) -> BouDePedra:
    """Create a BouDePedra boss entity."""
    arena_bounds = (0, 0, 400, 224)
    b = BouDePedra(200, 100, boss_definition, event_bus, arena_bounds)
    b.setup_pillars(boss_definition["arena"]["pillar_positions"])
    return b


@pytest.fixture
def player_rect() -> pygame.Rect:
    """Create a dummy player rect."""
    return pygame.Rect(50, 150, 24, 32)


# ── BossEntity base tests ─────────────────────────────────────────


class TestBossEntityInit:
    """Tests for BossEntity initialization."""

    def test_health_initialized(self, boss):
        assert boss.health == 30
        assert boss.max_health == 30

    def test_starts_in_intro_state(self, boss):
        assert boss.state == BossState.INTRO

    def test_display_name(self, boss):
        assert boss.display_name == "Es Bou de Pedra"

    def test_boss_id(self, boss):
        assert boss.boss_id == "bou_de_pedra"

    def test_starts_on_phase_1(self, boss):
        assert boss.current_phase == 1

    def test_health_fraction_full(self, boss):
        assert boss.health_fraction == 1.0

    def test_hitbox_dimensions(self, boss):
        assert boss.rect.width == 56
        assert boss.rect.height == 48

    def test_not_vulnerable_during_intro(self, boss):
        assert not boss.is_vulnerable


class TestBossStateTransitions:
    """Tests for boss state machine transitions."""

    def test_start_fight_transitions_to_idle(self, boss):
        boss.start_fight()
        assert boss.state == BossState.IDLE

    def test_idle_to_tell_after_duration(self, boss):
        boss.start_fight()
        # Advance past idle duration.
        boss.update(2.0)
        assert boss.state == BossState.TELL

    def test_tell_to_attacking(self, boss):
        boss.start_fight()
        boss.update(2.0)  # Idle -> Tell.
        tell_time = boss.current_pattern["tell_time"]
        boss.update(tell_time + 0.01)  # Tell -> Attacking.
        assert boss.state == BossState.ATTACKING

    def test_attacking_to_punish(self, boss):
        boss.start_fight()
        boss.update(2.0)  # Idle -> Tell.
        # Get through tell.
        pattern = boss.current_pattern
        boss.update(pattern["tell_time"] + 0.01)
        assert boss.state == BossState.ATTACKING
        # Get through attack.
        boss.update(10.0)  # Long dt to ensure attack finishes.
        assert boss.state == BossState.PUNISH

    def test_punish_to_idle(self, boss):
        boss.start_fight()
        # Run through a full attack cycle.
        boss.update(2.0)  # Idle -> Tell.
        boss.update(2.0)  # Tell -> Attacking.
        boss.update(10.0)  # Attacking -> Punish.
        punish_window = boss.current_pattern["punish_window"]
        boss.update(punish_window + 0.01)  # Punish -> Idle.
        assert boss.state == BossState.IDLE


class TestBossPhaseTransitions:
    """Tests for HP-threshold-based phase changes."""

    def test_phase_1_range(self, boss):
        assert boss.current_phase == 1

    def test_damage_below_66_triggers_phase_2(self, boss, event_bus):
        """When HP drops to 66% or below, phase 2 begins."""
        boss.start_fight()
        # Get boss into punish state (vulnerable).
        boss.update(2.0)  # Idle -> Tell.
        boss.update(2.0)  # Tell -> Attacking.
        boss.update(10.0)  # Attacking -> Punish.
        assert boss.state == BossState.PUNISH
        assert boss.is_vulnerable

        # Deal enough damage to drop below 66% (30 * 0.34 = ~10.2 damage).
        boss.take_damage(11.0)
        assert boss.state == BossState.PHASE_TRANSITION
        # After transition completes.
        boss.update(2.0)
        assert boss.current_phase == 2

    def test_damage_below_33_triggers_phase_3(self, boss):
        """When HP drops to 33% or below, phase 3 begins."""
        boss.start_fight()
        # Get to punish.
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)

        # Drop straight to phase 3 (below 33%).
        boss.take_damage(21.0)  # 30 - 21 = 9, which is 30% < 33%.
        assert boss.state == BossState.PHASE_TRANSITION
        boss.update(2.0)
        assert boss.current_phase == 3

    def test_phase_transition_makes_boss_invincible(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        boss.take_damage(11.0)
        assert boss.state == BossState.PHASE_TRANSITION
        assert not boss.is_vulnerable

    def test_phase_transition_publishes_event(self, boss, event_bus):
        received = []
        event_bus.subscribe("boss_phase_change", lambda **kw: received.append(kw))
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        boss.take_damage(11.0)
        assert len(received) == 1
        assert received[0]["old_phase"] == 1
        assert received[0]["new_phase"] == 2

    def test_core_exposed_in_phase_3(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        boss.take_damage(21.0)
        boss.update(2.0)  # Complete transition.
        assert boss.core_exposed


class TestBossVulnerability:
    """Tests for boss vulnerability logic."""

    def test_not_vulnerable_in_idle(self, boss):
        boss.start_fight()
        assert not boss.is_vulnerable

    def test_not_vulnerable_in_tell(self, boss):
        boss.start_fight()
        boss.update(2.0)
        assert boss.state == BossState.TELL
        assert not boss.is_vulnerable

    def test_not_vulnerable_in_attacking(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        assert boss.state == BossState.ATTACKING
        assert not boss.is_vulnerable

    def test_vulnerable_in_punish(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        assert boss.state == BossState.PUNISH
        assert boss.is_vulnerable

    def test_damage_rejected_outside_punish(self, boss):
        boss.start_fight()
        assert not boss.take_damage(5.0)
        assert boss.health == 30

    def test_damage_applied_in_punish(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        assert boss.take_damage(5.0)
        assert boss.health == 25


class TestBossDamageMultipliers:
    """Tests for Phase 3 weak point damage multipliers."""

    def test_tier2_charge_gets_2x_damage_on_core(self, boss):
        """Charged shots deal 2x damage to exposed core."""
        boss.start_fight()
        # Get to punish state first.
        boss.update(2.0)   # Idle -> Tell.
        boss.update(2.0)   # Tell -> Attacking.
        boss.update(10.0)  # Attacking -> Punish.
        assert boss.is_vulnerable

        # Jump to phase 3 with massive damage.
        boss.take_damage(21.0)
        boss.update(2.0)  # Complete transition to phase 3.
        assert boss.current_phase == 3
        assert boss.core_exposed

        # Get to punish in phase 3.
        boss.update(2.0)   # Idle -> Tell.
        boss.update(2.0)   # Tell -> Attacking.
        boss.update(10.0)  # Attacking -> Punish.
        assert boss.is_vulnerable

        hp_before = boss.health
        boss.take_damage(1.0, charge_tier=2)
        # Should deal 2.0 damage (1.0 * 2x multiplier).
        assert boss.health == pytest.approx(hp_before - 2.0)

    def test_tier3_charge_gets_3x_damage_on_core(self, boss):
        """Tier 3 charged shots deal 3x damage to exposed core."""
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        # Jump to phase 3.
        boss.take_damage(21.0)
        boss.update(2.0)  # Complete transition.
        assert boss.current_phase == 3
        assert boss.core_exposed

        # Get to punish in phase 3.
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        assert boss.is_vulnerable

        hp_before = boss.health
        boss.take_damage(1.0, charge_tier=3)
        assert boss.health == pytest.approx(hp_before - 3.0)

    def test_melee_no_multiplier_on_core(self, boss):
        """Melee (charge_tier=0) does NOT get weak point multiplier."""
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        # Jump to phase 3.
        boss.take_damage(21.0)
        boss.update(2.0)  # Complete transition.
        assert boss.current_phase == 3
        assert boss.core_exposed

        # Get to punish in phase 3.
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        assert boss.is_vulnerable

        hp_before = boss.health
        boss.take_damage(1.0, charge_tier=0)
        assert boss.health == pytest.approx(hp_before - 1.0)


class TestBossDefeat:
    """Tests for boss defeat."""

    def test_boss_defeated_at_zero_hp(self, boss, event_bus):
        received = []
        event_bus.subscribe("boss_defeated", lambda **kw: received.append(kw))

        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)

        # Kill the boss.
        boss.take_damage(30.0)
        assert boss.state == BossState.DEFEATED
        assert not boss.is_alive
        assert len(received) == 1
        assert received[0]["boss_id"] == "bou_de_pedra"

    def test_post_defeat_data(self, boss, event_bus):
        received = []
        event_bus.subscribe("boss_defeated", lambda **kw: received.append(kw))

        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        boss.take_damage(30.0)

        assert received[0]["post_defeat"]["mask_granted"] == "stone_slam"


class TestBossAttackTiming:
    """Tests for attack tell and punish timing."""

    def test_all_patterns_have_minimum_tell_time(self, boss_definition):
        """GDD rule: all attacks have minimum 0.5s tell time."""
        for phase in boss_definition["phases"]:
            for pattern in phase["patterns"]:
                assert pattern["tell_time"] >= 0.5, (
                    f"Pattern {pattern['id']} in phase {phase['phase']} "
                    f"has tell_time {pattern['tell_time']} < 0.5s"
                )

    def test_all_patterns_have_minimum_punish_window(self, boss_definition):
        """GDD rule: all attacks have minimum 1.5s punish window."""
        for phase in boss_definition["phases"]:
            for pattern in phase["patterns"]:
                assert pattern["punish_window"] >= 1.5, (
                    f"Pattern {pattern['id']} in phase {phase['phase']} "
                    f"has punish_window {pattern['punish_window']} < 1.5s"
                )


# ── BouDePedra specific tests ─────────────────────────────────────


class TestBouDePedraPillars:
    """Tests for destructible pillars."""

    def test_four_pillars_created(self, boss):
        assert len(boss.pillars) == 4

    def test_all_pillars_active(self, boss):
        assert all(p.active for p in boss.pillars)

    def test_pillar_destruction(self, boss):
        boss.pillars[0].active = False
        assert len(boss.active_pillars) == 3


class TestBouDePedraAttacks:
    """Tests for specific attack implementations."""

    def test_bull_rush_creates_movement(self, boss_definition, event_bus):
        """Bull Rush should set the boss to moving state."""
        # Place boss far from any pillar to avoid collision on first frame.
        arena_bounds = (0, 0, 800, 224)
        boss = BouDePedra(400, 100, boss_definition, event_bus, arena_bounds)
        # No pillars -- just testing movement.
        boss.start_fight()

        rush_pattern = {
            "id": "bull_rush",
            "tell_time": 1.0,
            "damage": 1.5,
            "punish_window": 2.5,
            "weight": 1.0,
            "params": {"speed": 200, "stun_on_wall_hit": True, "destroys_pillars": True},
        }
        player_rect = pygame.Rect(50, 150, 24, 32)
        boss._current_pattern = rush_pattern
        boss._state = BossState.ATTACKING
        boss._state_timer = 5.0
        boss._start_bull_rush(rush_pattern["params"])

        boss.update_with_player(player_rect, 0.02)
        assert boss.state == BossState.ATTACKING
        assert boss._moving

    def test_headbutt_creates_projectile(self, boss, player_rect):
        boss.start_fight()
        boss._player_rect = player_rect

        # Force headbutt attack.
        headbutt = {
            "id": "headbutt",
            "tell_time": 0.5,
            "damage": 1.0,
            "punish_window": 1.5,
            "params": {"range": 2.0},
        }
        boss._current_pattern = headbutt
        boss._state = BossState.TELL
        boss._state_timer = 0.01

        boss.update_with_player(player_rect, 0.02)
        # Should have spawned a melee hitbox projectile.
        assert len(boss.projectiles) >= 1

    def test_ground_stomp_creates_shockwaves(self, boss, player_rect):
        boss.start_fight()
        boss._player_rect = player_rect

        stomp = {
            "id": "ground_stomp",
            "tell_time": 1.2,
            "damage": 1.0,
            "punish_window": 2.0,
            "params": {"shockwave_range": 6, "direct_damage": 1.5},
        }
        boss._current_pattern = stomp
        boss._state = BossState.TELL
        boss._state_timer = 0.01

        boss.update_with_player(player_rect, 0.02)
        # Two shockwaves (left and right).
        shockwaves = [p for p in boss.projectiles if p.proj_type == "shockwave"]
        assert len(shockwaves) == 2

    def test_rock_hurl_creates_rocks_and_markers(self, boss, player_rect):
        boss.start_fight()
        boss._player_rect = player_rect

        hurl = {
            "id": "rock_hurl",
            "tell_time": 0.8,
            "damage": 1.0,
            "punish_window": 1.5,
            "params": {"rock_count": 3},
        }
        boss._current_pattern = hurl
        boss._state = BossState.TELL
        boss._state_timer = 0.01

        boss.update_with_player(player_rect, 0.02)
        rocks = [p for p in boss.projectiles if p.proj_type == "rock"]
        assert len(rocks) == 3
        assert len(boss.shadow_markers) == 3

    def test_core_pulse_creates_pulse_projectiles(self, boss, player_rect):
        boss.start_fight()
        boss._player_rect = player_rect

        pulse = {
            "id": "core_pulse",
            "tell_time": 1.0,
            "damage": 1.0,
            "punish_window": 2.0,
            "params": {"radius": 8},
        }
        boss._current_pattern = pulse
        boss._state = BossState.TELL
        boss._state_timer = 0.01

        boss.update_with_player(player_rect, 0.02)
        pulses = [p for p in boss.projectiles if p.proj_type == "pulse"]
        assert len(pulses) == 2  # Left and right.


class TestBouDePedraWallCollision:
    """Tests for wall collision during rushes."""

    def test_bull_rush_wall_hit_forces_punish(self, boss, player_rect):
        """Bull Rush hitting a wall should stun the boss (punish window)."""
        boss.start_fight()
        boss._player_rect = player_rect

        rush = {
            "id": "bull_rush",
            "tell_time": 1.0,
            "damage": 1.5,
            "punish_window": 2.5,
            "params": {"speed": 200},
        }
        boss._current_pattern = rush
        boss._state = BossState.ATTACKING
        boss._state_timer = 5.0
        boss._moving = True
        boss._move_direction = -1.0
        boss._move_speed = 200

        # Move boss to left wall.
        boss._sub_x = 10.0
        boss.rect.x = 10
        boss.update_with_player(player_rect, 0.1)

        # Should have hit left wall and entered punish.
        assert not boss._moving

    def test_frenzy_rush_bounces_off_walls(self, boss, player_rect):
        """Frenzy Rush should bounce off walls and keep going."""
        boss.start_fight()
        boss._player_rect = player_rect

        frenzy = {
            "id": "frenzy_rush",
            "tell_time": 0.6,
            "damage": 1.5,
            "punish_window": 2.5,
            "params": {"speed": 280, "bounces": 3},
        }
        boss._current_pattern = frenzy
        boss._state = BossState.ATTACKING
        boss._state_timer = 20.0
        boss._moving = True
        boss._move_direction = -1.0
        boss._move_speed = 280
        boss._rush_bounces_remaining = 3

        # Simulate wall hit.
        boss._sub_x = 1.0
        boss.rect.x = 1
        boss.update_with_player(player_rect, 0.05)

        # Should have bounced (direction reversed, still moving).
        assert boss._move_direction == 1.0
        assert boss._moving
        assert boss._rush_bounces_remaining == 2


class TestBouDePedraAttackRects:
    """Tests for attack hitbox generation."""

    def test_no_attack_rects_when_idle(self, boss):
        boss.start_fight()
        assert len(boss.get_attack_rects()) == 0

    def test_rush_body_is_attack_rect(self, boss, player_rect):
        boss.start_fight()
        boss._state = BossState.ATTACKING
        boss._moving = True
        boss._current_pattern = {"id": "bull_rush", "damage": 1.5}
        rects = boss.get_attack_rects()
        assert len(rects) >= 1
        assert rects[0][1] == 1.5  # Damage value.


# ── BossProjectile tests ──────────────────────────────────────────


class TestBossProjectile:
    """Tests for boss projectile behavior."""

    def test_projectile_moves(self):
        proj = BossProjectile(100, 100, 8, 8, 200, 0, 1.0, 2.0)
        proj.update(0.5)
        assert proj.rect.x > 100

    def test_projectile_expires(self):
        proj = BossProjectile(100, 100, 8, 8, 200, 0, 1.0, 0.5)
        proj.update(0.6)
        assert not proj.active

    def test_projectile_damage(self):
        proj = BossProjectile(100, 100, 8, 8, 0, 0, 1.5, 2.0)
        assert proj.damage == 1.5


class TestShadowMarker:
    """Tests for shadow marker behavior."""

    def test_marker_expires(self):
        marker = ShadowMarker(100, 200, 0.8)
        marker.update(0.9)
        assert not marker.active

    def test_marker_active_during_duration(self):
        marker = ShadowMarker(100, 200, 0.8)
        marker.update(0.5)
        assert marker.active


class TestDestructiblePillar:
    """Tests for destructible pillar behavior."""

    def test_pillar_starts_active(self):
        pillar = DestructiblePillar(100, 100)
        assert pillar.active

    def test_pillar_has_rect(self):
        pillar = DestructiblePillar(100, 100)
        assert pillar.rect.width == 16
        assert pillar.rect.height == 48  # 3 tiles tall.


# ── BossHealthBar tests ──────────────────────────────────────────


class TestBossHealthBar:
    """Tests for the boss health bar UI component."""

    def test_initial_state(self):
        bar = BossHealthBar("Test Boss", 30.0)
        assert bar.health_fraction == 1.0
        assert bar.current_health == 30.0
        assert bar.max_health == 30.0

    def test_set_health_updates_fraction(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_health(15.0)
        assert bar.health_fraction == 0.5

    def test_set_health_zero(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_health(0.0)
        assert bar.health_fraction == 0.0

    def test_set_health_negative_clamps(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_health(-5.0)
        assert bar.health_fraction == 0.0

    def test_display_health_catches_up(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_health(15.0)
        # Display health should still be at max until animated.
        assert bar.display_fraction == 1.0
        # After update, display health should start catching up.
        bar.update(1.0)
        assert bar.display_fraction < 1.0

    def test_phase_change_triggers_flash(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_phase(2, "The Stomp")
        assert bar._flash_timer > 0

    def test_visibility(self):
        bar = BossHealthBar("Test Boss", 30.0)
        assert bar.visible
        bar.visible = False
        assert not bar.visible

    def test_renders_without_error(self):
        bar = BossHealthBar("Test Boss", 30.0, [0.66, 0.33])
        surface = pygame.Surface((384, 216))
        bar.render(surface)
        # No exception = pass.

    def test_renders_at_half_health(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.set_health(15.0)
        bar.update(5.0)  # Let display catch up.
        surface = pygame.Surface((384, 216))
        bar.render(surface)

    def test_renders_when_invisible(self):
        bar = BossHealthBar("Test Boss", 30.0)
        bar.visible = False
        surface = pygame.Surface((384, 216))
        bar.render(surface)
        # Should not crash even when invisible.


# ── BossEntity rendering tests ────────────────────────────────────


class TestBossRendering:
    """Tests for boss entity rendering."""

    def test_renders_in_idle(self, boss):
        boss.start_fight()
        surface = pygame.Surface((384, 216))
        boss.render(surface, (0, 0))

    def test_renders_in_tell(self, boss):
        boss.start_fight()
        boss.update(2.0)
        surface = pygame.Surface((384, 216))
        boss.render(surface, (0, 0))

    def test_renders_in_punish(self, boss):
        boss.start_fight()
        boss.update(2.0)
        boss.update(2.0)
        boss.update(10.0)
        surface = pygame.Surface((384, 216))
        boss.render(surface, (0, 0))

    def test_renders_with_core_exposed(self, boss):
        boss._core_exposed = True
        boss.start_fight()
        surface = pygame.Surface((384, 216))
        boss.render(surface, (0, 0))

    def test_pillar_renders(self):
        pillar = DestructiblePillar(50, 100)
        surface = pygame.Surface((384, 216))
        pillar.render(surface, (0, 0))


# ── JSON loading test ─────────────────────────────────────────────


class TestBossDefinitionLoading:
    """Tests for loading boss definitions from JSON."""

    def test_load_bou_de_pedra_json(self):
        """Load the actual boss JSON file."""
        definition = BossEntity.load_definition("bou_de_pedra")
        assert definition["boss_id"] == "bou_de_pedra"
        assert definition["health"] == 30
        assert len(definition["phases"]) == 3

    def test_loaded_definition_has_all_phases(self):
        definition = BossEntity.load_definition("bou_de_pedra")
        phase_names = [p["name"] for p in definition["phases"]]
        assert phase_names == ["The Charge", "The Stomp", "The Core"]

    def test_loaded_definition_has_weak_point(self):
        definition = BossEntity.load_definition("bou_de_pedra")
        phase3 = definition["phases"][2]
        assert phase3["weak_point"]["charge_multiplier"] == 2.0
        assert phase3["weak_point"]["tier3_multiplier"] == 3.0


# ── Integration: full attack cycle ────────────────────────────────


class TestFullAttackCycle:
    """Integration test for a complete attack cycle."""

    def test_complete_cycle_idle_tell_attack_punish_idle(self, boss, player_rect):
        """Verify the full boss attack cycle."""
        boss.start_fight()
        boss._player_rect = player_rect

        # 1. Start in idle.
        assert boss.state == BossState.IDLE

        # 2. Advance to tell.
        boss.update_with_player(player_rect, 2.0)
        assert boss.state == BossState.TELL
        pattern = boss.current_pattern
        assert pattern is not None

        # 3. Advance through tell to attacking.
        boss.update_with_player(player_rect, pattern["tell_time"] + 0.01)
        assert boss.state == BossState.ATTACKING

        # 4. Advance through attacking to punish.
        boss.update_with_player(player_rect, 20.0)
        assert boss.state == BossState.PUNISH
        assert boss.is_vulnerable

        # 5. Deal damage during punish.
        boss.take_damage(2.0)
        assert boss.health == 28

        # 6. Advance through punish to idle.
        boss.update_with_player(player_rect, pattern["punish_window"] + 0.01)
        assert boss.state == BossState.IDLE


class TestBossDoesNotRepeatPattern:
    """Test that the boss avoids repeating the same pattern."""

    def test_pattern_selection_avoids_repeat(self, boss):
        """The boss should try to avoid using the same pattern twice."""
        boss.start_fight()
        boss._last_pattern_id = "bull_rush"

        # With only 2 patterns in phase 1, the next should prefer headbutt.
        selections = set()
        for _ in range(20):
            pattern = boss._select_next_pattern()
            if pattern:
                selections.add(pattern["id"])

        # Should have at least selected headbutt at some point.
        assert "headbutt" in selections


# ── Boss Registry tests ──────────────────────────────────────────


class TestBossRegistry:
    """Tests for the boss registry/factory."""

    def test_get_bou_de_pedra_class(self):
        from sa_fona.entities.bosses import get_boss_class

        cls = get_boss_class("bou_de_pedra")
        assert cls is BouDePedra

    def test_unknown_boss_id_raises(self):
        from sa_fona.entities.bosses import get_boss_class

        with pytest.raises(ValueError, match="Unknown boss_id"):
            get_boss_class("nonexistent_boss")


# ── BossScene integration tests ──────────────────────────────────


class TestBossSceneInit:
    """Tests for BossScene instantiation."""

    def test_scene_instantiates_with_defaults(self):
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        assert scene.player is not None
        assert scene.boss is not None
        assert scene.boss_health_bar is not None
        assert scene.combat is not None

    def test_scene_instantiates_with_event_bus(self):
        from sa_fona.scenes.boss_scene import BossScene

        bus = EventBus()
        scene = BossScene(boss_id="bou_de_pedra", event_bus=bus)
        assert scene.boss.boss_id == "bou_de_pedra"

    def test_scene_boss_starts_in_intro(self):
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        assert scene.boss.state == BossState.INTRO
        assert not scene.fight_started

    def test_scene_loads_cave_tileset(self):
        """Arena tilemap uses the cave tileset from the boss definition."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        # The tilemap should have a tileset loaded (non-empty tile list).
        assert scene._tilemap._tileset_surface is not None
        assert len(scene._tilemap._tileset_tiles) > 0

    def test_scene_tilemap_has_cave_metadata(self):
        """Arena tilemap metadata identifies the cave tileset."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        # The highlight color should be the cave variant (cool tone).
        from sa_fona.level.tilemap import HIGHLIGHT_COLOR_CAVE
        assert scene._tilemap._highlight_color == HIGHLIGHT_COLOR_CAVE


class TestBossSceneUpdateLoop:
    """Tests that the BossScene update loop runs without errors."""

    def test_update_runs_intro_frames(self):
        """Simulate several frames during the intro phase."""
        from sa_fona.scenes.boss_scene import BossScene
        from sa_fona.core.input_handler import InputState

        scene = BossScene()
        scene.on_enter()
        dt = 1.0 / 60.0
        for _ in range(30):
            scene.handle_input(InputState())
            scene.update(dt)
        # Boss should still be in intro or just transitioned.
        # No exceptions means success.

    def test_update_runs_fight_frames(self):
        """Simulate frames after the fight starts."""
        from sa_fona.scenes.boss_scene import BossScene
        from sa_fona.core.input_handler import InputState

        scene = BossScene()
        scene.on_enter()
        dt = 1.0 / 60.0

        # Burn through the intro.
        for _ in range(150):
            scene.handle_input(InputState())
            scene.update(dt)

        assert scene.fight_started
        # Run fight frames.
        for _ in range(60):
            scene.handle_input(InputState())
            scene.update(dt)

    def test_render_does_not_crash(self):
        """Render the scene without errors."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene.on_enter()
        surface = pygame.Surface((384, 216))
        scene.update(1.0 / 60.0)
        scene.render(surface)


class TestBossSceneDamage:
    """Tests for boss damage through BossScene combat integration."""

    def test_boss_takes_damage_during_punish_window(self):
        """Verify that the boss can be damaged through the scene during punish."""
        from sa_fona.scenes.boss_scene import BossScene
        from sa_fona.core.input_handler import InputState

        scene = BossScene()
        scene.on_enter()
        dt = 1.0 / 60.0

        # Burn through intro.
        for _ in range(150):
            scene.handle_input(InputState())
            scene.update(dt)

        assert scene.fight_started

        # Force the boss into punish state for direct damage test.
        scene.boss.start_fight()
        scene.boss.update(2.0)   # Idle -> Tell.
        scene.boss.update(2.0)   # Tell -> Attacking.
        scene.boss.update(10.0)  # Attacking -> Punish.
        assert scene.boss.state == BossState.PUNISH
        assert scene.boss.is_vulnerable

        hp_before = scene.boss.health
        scene.boss.take_damage(3.0)
        assert scene.boss.health == hp_before - 3.0

    def test_player_takes_damage_via_public_api(self):
        """Verify that deal_damage_to_player() works through the scene."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene.on_enter()

        hearts_before = scene.combat.player_hearts
        scene.combat.deal_damage_to_player(1.0)
        assert scene.combat.player_hearts == hearts_before - 1.0
        assert scene.combat.player_invincible

    def test_cleanup_does_not_crash(self):
        """Verify that on_exit cleans up without errors."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene.on_enter()
        scene.update(1.0 / 60.0)
        scene.on_exit()


class TestBossSceneBackground:
    """Tests for boss scene background rendering."""

    def test_background_loaded_from_definition(self):
        """BossScene loads the background image when specified in arena data."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        # The boss_bou_de_pedra.json specifies "background": "world1_cave",
        # and the asset should exist.
        assert scene._background is not None

    def test_render_background_with_image(self):
        """_render_background draws without error when background is loaded."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        surface = pygame.Surface((384, 216))
        scene._render_background(surface)
        # No exception = pass.

    def test_render_background_fallback_no_image(self):
        """_render_background falls back to solid fill when no background."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene._background = None  # Force no background.
        surface = pygame.Surface((384, 216))
        scene._render_background(surface)
        # No exception = pass.

    def test_full_render_with_background(self):
        """Full render pipeline works with background image."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene.on_enter()
        scene.update(1.0 / 60.0)
        surface = pygame.Surface((384, 216))
        scene.render(surface)


# ── Player-Pillar collision tests ────────────────────────────────


class TestPillarCollision:
    """Tests for player-pillar AABB collision in BossScene."""

    @staticmethod
    def _make_scene():
        """Create a BossScene for pillar collision testing."""
        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene()
        scene.on_enter()
        # Burn through intro so fight_started is True.
        dt = 1.0 / 60.0
        for _ in range(150):
            from sa_fona.core.input_handler import InputState
            scene.handle_input(InputState())
            scene.update(dt)
        assert scene.fight_started
        return scene

    def test_horizontal_block_from_left(self):
        """Player walking right into a pillar is stopped."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Position player just to the left of the pillar, overlapping.
        player.rect.right = pillar.rect.left + 4  # 4px overlap
        player.rect.centery = pillar.rect.centery
        player.velocity[0] = 80.0
        player.velocity[1] = 0.0

        on_ground = scene._resolve_pillar_collision(False)
        assert player.rect.right <= pillar.rect.left
        assert player.velocity[0] == 0.0

    def test_horizontal_block_from_right(self):
        """Player walking left into a pillar is stopped."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Position player just to the right of the pillar, overlapping.
        player.rect.left = pillar.rect.right - 4  # 4px overlap
        player.rect.centery = pillar.rect.centery
        player.velocity[0] = -80.0
        player.velocity[1] = 0.0

        on_ground = scene._resolve_pillar_collision(False)
        assert player.rect.left >= pillar.rect.right
        assert player.velocity[0] == 0.0

    def test_land_on_pillar_top(self):
        """Player falling onto a pillar top becomes on_ground."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Position player above the pillar, overlapping top by 3px.
        player.rect.bottom = pillar.rect.top + 3
        player.rect.centerx = pillar.rect.centerx
        player.velocity[0] = 0.0
        player.velocity[1] = 100.0  # Falling down.

        on_ground = scene._resolve_pillar_collision(False)
        assert on_ground is True
        assert player.rect.bottom <= pillar.rect.top
        assert player.velocity[1] == 0.0

    def test_head_bump_on_pillar_bottom(self):
        """Player jumping up into a pillar bottom stops upward velocity."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Position player below the pillar, overlapping bottom by 3px.
        player.rect.top = pillar.rect.bottom - 3
        player.rect.centerx = pillar.rect.centerx
        player.velocity[0] = 0.0
        player.velocity[1] = -150.0  # Moving up.

        on_ground = scene._resolve_pillar_collision(False)
        assert player.rect.top >= pillar.rect.bottom
        assert player.velocity[1] == 0.0
        assert on_ground is False  # Should not set on_ground.

    def test_inactive_pillar_no_collision(self):
        """Destroyed pillars do not block the player."""
        scene = self._make_scene()
        pillar = scene.boss.pillars[0]
        player = scene.player

        # Destroy the pillar.
        pillar.active = False

        # Position player overlapping the pillar.
        player.rect.centerx = pillar.rect.centerx
        player.rect.centery = pillar.rect.centery
        original_x = player.rect.x
        player.velocity[0] = 50.0

        on_ground = scene._resolve_pillar_collision(False)
        # Player should not have been pushed.
        assert player.rect.x == original_x

    def test_wall_contact_detects_pillar(self):
        """Wall contact probes detect active pillars."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Place player flush against the left side of the pillar.
        player.rect.right = pillar.rect.left
        player.rect.centery = pillar.rect.centery

        wall_left, wall_right = scene._check_wall_contact(player.rect)
        assert wall_right is True

    def test_wall_contact_ignores_inactive_pillar(self):
        """Wall contact probes do not detect destroyed pillars."""
        scene = self._make_scene()
        pillar = scene.boss.pillars[0]
        player = scene.player

        pillar.active = False

        # Place player flush against the left side of the pillar.
        player.rect.right = pillar.rect.left
        player.rect.centery = pillar.rect.centery

        # Check that the pillar is not detected as a wall
        # (we need to ensure the player is not near any tile wall either).
        # Move player to an open area far from tile walls.
        player.rect.x = pillar.rect.left - player.rect.width
        player.rect.centery = pillar.rect.centery

        wall_left, wall_right = scene._check_wall_contact(player.rect)
        # The destroyed pillar should not register as a wall.
        assert not wall_right
        # (wall_right could still be True if near a tile wall.)

    def test_corner_case_no_glitch(self):
        """Player at pillar corner does not teleport or glitch."""
        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]
        player = scene.player

        # Position player at the corner of the pillar with diagonal velocity.
        player.rect.right = pillar.rect.left + 2
        player.rect.bottom = pillar.rect.top + 2
        player.velocity[0] = 60.0
        player.velocity[1] = 80.0

        old_x = player.rect.x
        old_y = player.rect.y
        on_ground = scene._resolve_pillar_collision(False)

        # Player should have been pushed out (not inside the pillar).
        assert not player.rect.colliderect(pillar.rect)
        # Player should not have teleported far away.
        assert abs(player.rect.x - old_x) < 20
        assert abs(player.rect.y - old_y) < 20

    def test_update_loop_with_pillars_no_crash(self):
        """Full update loop with player near pillars does not crash."""
        from sa_fona.core.input_handler import InputState

        scene = self._make_scene()
        pillar = scene.boss.active_pillars[0]

        # Position player on top of the pillar.
        scene.player.rect.bottom = pillar.rect.top
        scene.player.rect.centerx = pillar.rect.centerx
        scene.player.velocity = [0.0, 0.0]

        dt = 1.0 / 60.0
        for _ in range(60):
            scene.handle_input(InputState())
            scene.update(dt)
        # No crash = pass.
