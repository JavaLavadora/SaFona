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
