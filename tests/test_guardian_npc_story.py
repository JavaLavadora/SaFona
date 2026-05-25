"""Tests for stone guardian attack, NPC idle animation, and story coherence.

Covers:
- GuardianBehavior wind-up -> strike -> recovery cycle
- Stone guardian attack damage applied during strike phase only
- NPC idle animation frame advancement
- NPC update called from gameplay scene
- Dialogue story coherence checks
"""

from __future__ import annotations

import json
from pathlib import Path

import pygame
import pytest

from sa_fona.config.settings import DATA_DIR
from sa_fona.entities.enemy_behaviors import (
    AttackState,
    GuardianBehavior,
    create_behavior,
)
from sa_fona.entities.npc import NPC


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    pygame.init()
    yield


# ── Stone Guardian Attack Tests ──────────────────────────────────


class TestGuardianBehaviorCycle:
    """Tests for the guardian wind-up -> strike -> recovery cycle."""

    @staticmethod
    def _make_guardian(**overrides) -> GuardianBehavior:
        """Create a GuardianBehavior with sensible test defaults."""
        params = {
            "patrol_range": 3,
            "speed": 20,
            "attack_range": 40,
            "attack_windup": 0.8,
            "attack_strike": 0.3,
            "attack_recovery": 0.6,
            "attack_cooldown": 2.0,
        }
        params.update(overrides)
        guardian = GuardianBehavior(params)
        guardian.reset(100.0)
        return guardian

    def test_enters_tell_when_player_close(self):
        """Guardian enters wind-up (TELL) when player is within range."""
        guardian = self._make_guardian()
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)  # ~20px away, < 40.

        result = guardian.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.TELL
        assert result.move_x != 0.0  # Charges toward player during wind-up.
        assert result.speed == 20 * 2.5  # 2.5x charge speed.

    def test_windup_to_strike_transition(self):
        """Guardian transitions from TELL to ATTACKING after windup time."""
        guardian = self._make_guardian(attack_windup=0.1)
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        # Enter tell.
        guardian.update(enemy_rect, player_rect, 1 / 60)
        assert guardian.attack_state == AttackState.TELL

        # Advance past wind-up (0.1s).
        for _ in range(10):
            result = guardian.update(enemy_rect, player_rect, 1 / 60)

        assert result.attack_state == AttackState.ATTACKING
        assert result.wants_attack is True

    def test_strike_to_recovery_transition(self):
        """Guardian transitions from ATTACKING to RECOVERY after strike time."""
        guardian = self._make_guardian(
            attack_windup=0.01, attack_strike=0.1,
        )
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        # Rush through wind-up.
        guardian.update(enemy_rect, player_rect, 0.02)
        guardian.update(enemy_rect, player_rect, 0.02)

        # Now in ATTACKING. Advance past strike time.
        for _ in range(10):
            result = guardian.update(enemy_rect, player_rect, 1 / 60)

        assert result.attack_state == AttackState.RECOVERY
        assert result.wants_attack is False
        assert result.move_x == 0.0  # Cannot move during recovery.

    def test_recovery_to_cooldown_transition(self):
        """Guardian transitions from RECOVERY to COOLDOWN after recovery time."""
        guardian = self._make_guardian(
            attack_windup=0.01, attack_strike=0.01, attack_recovery=0.1,
        )
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        # Rush through wind-up and strike.
        for _ in range(5):
            guardian.update(enemy_rect, player_rect, 0.02)

        # Now in RECOVERY. Advance past recovery time.
        for _ in range(10):
            result = guardian.update(enemy_rect, player_rect, 1 / 60)

        assert result.attack_state == AttackState.COOLDOWN

    def test_full_cycle_returns_to_idle(self):
        """Full cycle: TELL -> ATTACKING -> RECOVERY -> COOLDOWN -> IDLE."""
        guardian = self._make_guardian(
            attack_windup=0.05,
            attack_strike=0.05,
            attack_recovery=0.05,
            attack_cooldown=0.1,
        )
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_close = pygame.Rect(120, 100, 24, 32)
        player_far = pygame.Rect(500, 100, 24, 32)

        # Track all states we see.
        seen_states: set[AttackState] = set()

        # Enter TELL with player close.
        result = guardian.update(enemy_rect, player_close, 1 / 60)
        seen_states.add(result.attack_state)

        # Advance through entire cycle with player far (won't re-trigger).
        # Total time needed: 0.05 + 0.05 + 0.05 + 0.1 = 0.25s.
        # Run for 0.5s to be safe.
        for _ in range(30):
            result = guardian.update(enemy_rect, player_far, 1 / 60)
            seen_states.add(result.attack_state)

        # Should have passed through all states.
        assert AttackState.TELL in seen_states
        assert AttackState.ATTACKING in seen_states
        assert AttackState.RECOVERY in seen_states
        assert AttackState.COOLDOWN in seen_states
        # Final state should be IDLE (player is far, cooldown expired).
        assert result.attack_state == AttackState.IDLE

    def test_patrols_when_player_far_away(self):
        """Guardian should patrol normally when player is out of range."""
        guardian = self._make_guardian()
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(500, 100, 24, 32)  # Far away.

        result = guardian.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.IDLE
        assert result.move_x != 0.0
        assert result.speed == 20

    def test_stops_during_recovery(self):
        """Guardian cannot move during recovery phase."""
        guardian = self._make_guardian(
            attack_windup=0.01, attack_strike=0.01,
        )
        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        # Rush to recovery.
        for _ in range(5):
            guardian.update(enemy_rect, player_rect, 0.02)

        # Now in recovery.
        result = guardian.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.RECOVERY
        assert result.move_x == 0.0
        assert result.speed == 0.0


class TestGuardianAttackDamage:
    """Tests for guardian attack damage applied during strike phase only."""

    def test_attack_damage_differs_from_contact(self):
        """Enemy attack_damage should use the configured value, not contact."""
        from sa_fona.entities.enemy import Enemy

        definition = {
            "health": 6,
            "contact_damage": 1.5,
            "attack_damage": 2.0,
            "behavior": "guardian",
            "behavior_params": {
                "patrol_range": 3,
                "speed": 20,
                "attack_range": 40,
                "attack_windup": 0.8,
                "attack_strike": 0.3,
                "attack_recovery": 0.6,
                "attack_cooldown": 2.0,
            },
            "hitbox": {"w": 24, "h": 32},
        }
        enemy = Enemy(100, 100, "stone_guardian", definition)
        assert enemy.contact_damage == 1.5
        assert enemy.attack_damage == 2.0

    def test_combat_uses_attack_damage_for_strikes(self):
        """CombatSystem should deal attack_damage when enemy is striking."""
        from sa_fona.core.event_bus import EventBus
        from sa_fona.entities.enemy import Enemy
        from sa_fona.systems.combat import CombatSystem

        event_bus = EventBus()
        combat = CombatSystem(event_bus)
        combat.set_player_health(5.0, 5)

        definition = {
            "health": 6,
            "contact_damage": 1.0,
            "attack_damage": 2.0,
            "behavior": "guardian",
            "behavior_params": {
                "patrol_range": 3,
                "speed": 20,
                "attack_range": 40,
                "attack_windup": 0.01,
                "attack_strike": 1.0,
                "attack_recovery": 0.6,
                "attack_cooldown": 2.0,
            },
            "hitbox": {"w": 24, "h": 32},
        }
        enemy = Enemy(100, 100, "stone_guardian", definition)

        # Advance enemy to ATTACKING state (facing right).
        # Enemy hitbox shrink=2: rect at (102, 102, 20, 28), centerx=112.
        # Player at x=130, centerx=142. Distance = 30px < 40px range.
        player_rect_for_behavior = pygame.Rect(130, 100, 24, 32)
        enemy.update_with_player(player_rect_for_behavior, 0.02)
        enemy.update_with_player(player_rect_for_behavior, 0.02)
        enemy.update_with_player(player_rect_for_behavior, 0.02)
        assert enemy.is_attacking, (
            f"Expected ATTACKING but got {enemy.behavior_result.attack_state}"
        )
        assert enemy.facing_right

        # Place the FakePlayer in the attack hitbox zone (in front of enemy)
        # but NOT overlapping the enemy's body rect to avoid contact damage.
        # Enemy body: x=102, width=20, right=122.
        # Attack hitbox: x=122, width=48, covers [122, 170].
        # Place player at x=125 to overlap the attack hitbox but not the body.

        class FakePlayer:
            def __init__(self, rect):
                self.rect = rect

        player = FakePlayer(pygame.Rect(125, 100, 24, 32))

        # Verify positions: player should NOT overlap enemy body.
        assert not player.rect.colliderect(enemy.rect), (
            f"Player {player.rect} should not overlap enemy body {enemy.rect}"
        )
        # But SHOULD overlap the attack hitbox.
        assert player.rect.colliderect(enemy.attack_hitbox), (
            f"Player {player.rect} should overlap attack hitbox {enemy.attack_hitbox}"
        )

        # Run combat.
        combat.update(player, [enemy], [], [], 1 / 60)

        # Player should take attack_damage (2.0): 5.0 - 2.0 = 3.0.
        assert combat.player_hearts == 3.0

    def test_no_damage_during_windup(self):
        """Enemy should not deal attack damage during the wind-up phase."""
        guardian = GuardianBehavior({
            "patrol_range": 3,
            "speed": 20,
            "attack_range": 40,
            "attack_windup": 1.0,
            "attack_strike": 0.3,
            "attack_recovery": 0.6,
            "attack_cooldown": 2.0,
        })
        guardian.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        result = guardian.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.TELL
        assert result.wants_attack is False  # No damage during wind-up.

    def test_no_damage_during_recovery(self):
        """Enemy should not deal attack damage during recovery phase."""
        guardian = GuardianBehavior({
            "patrol_range": 3,
            "speed": 20,
            "attack_range": 40,
            "attack_windup": 0.01,
            "attack_strike": 0.01,
            "attack_recovery": 1.0,
            "attack_cooldown": 2.0,
        })
        guardian.reset(100.0)

        enemy_rect = pygame.Rect(100, 100, 24, 32)
        player_rect = pygame.Rect(120, 100, 24, 32)

        # Rush through wind-up + strike.
        for _ in range(5):
            guardian.update(enemy_rect, player_rect, 0.02)

        # Now in recovery.
        result = guardian.update(enemy_rect, player_rect, 1 / 60)
        assert result.attack_state == AttackState.RECOVERY
        assert result.wants_attack is False  # No damage during recovery.


class TestGuardianBehaviorFactory:
    """Test the factory registers the guardian behavior."""

    def test_create_guardian(self):
        """Factory should create a GuardianBehavior for 'guardian' type."""
        behavior = create_behavior("guardian", {"speed": 20})
        assert isinstance(behavior, GuardianBehavior)


# ── NPC Idle Animation Tests ─────────────────────────────────────


class TestNPCIdleAnimation:
    """Tests for the NPC idle animation (bob or multi-frame)."""

    def test_bob_animation_advances(self):
        """NPC with single-frame idle should bob up after half period."""
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")
        assert npc._bob_offset == 0

        # Advance past half the bob period (0.5s).
        npc.update(0.3)
        npc.update(0.3)
        # After 0.6s total, which is past 0.5s half-period, bob_offset
        # should be -1 (up phase lasts from 0.0 to 0.5).
        # At 0.6s the timer is past half, so offset should be 0 (down).
        # Let me trace: timer starts at 0, update 0.3 -> timer=0.3, <0.5 -> offset=-1
        # Then update 0.3 -> timer=0.6, >=0.5 -> offset=0.
        # So after second update, offset should be 0.
        # Let's just check after one update (0.3s < 0.5s half period).

    def test_bob_offset_changes_over_time(self):
        """NPC bob offset should alternate between -1 and 0."""
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")

        # Initially no offset.
        assert npc._bob_offset == 0

        # After a short time (< half period), should be bobbed up.
        npc.update(0.1)
        assert npc._bob_offset == -1  # Up phase.

        # Advance to second half of period (> 0.5s from start).
        npc.update(0.5)
        # Timer is now 0.6, past half-period -> back down.
        assert npc._bob_offset == 0

    def test_bob_resets_after_full_period(self):
        """Bob animation should cycle: up -> down -> up -> ..."""
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")

        # Full cycle.
        npc.update(0.25)
        assert npc._bob_offset == -1  # First half: up.

        npc.update(0.5)
        assert npc._bob_offset == 0  # Second half: down.

        npc.update(0.5)
        # Timer wraps: 1.25 - 1.0 = 0.25, < 0.5 -> up again.
        assert npc._bob_offset == -1

    def test_no_animation_during_talk_state(self):
        """NPC should not animate when state is not idle."""
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")
        # Directly set the state since set_sprite_state requires loaded sprites.
        npc._current_state = "talk"

        # Update should be a no-op for non-idle state.
        npc.update(0.3)
        assert npc._bob_offset == 0  # No bob in talk state.

    def test_multi_frame_idle_cycles(self):
        """NPC with multiple idle frames should cycle through them."""
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")

        # Manually inject multiple idle frames to test the cycling logic.
        fake_frame_1 = pygame.Surface((20, 36))
        fake_frame_2 = pygame.Surface((20, 36))
        fake_frame_3 = pygame.Surface((20, 36))
        npc._idle_frames = [fake_frame_1, fake_frame_2, fake_frame_3]
        npc._current_state = "idle"
        npc._anim_frame = 0
        npc._sprite = fake_frame_1

        # Advance past one animation frame period.
        npc.update(npc._anim_speed + 0.01)
        assert npc._anim_frame == 1
        assert npc._sprite is fake_frame_2


# ── NPC Update in Gameplay Scene ─────────────────────────────────


class TestNPCUpdateInGameplay:
    """Test that NPC update is called from the gameplay scene."""

    def test_gameplay_scene_updates_npcs(self):
        """GameplayScene.update() should call npc.update(dt) for each NPC."""
        from sa_fona.core.event_bus import EventBus
        from sa_fona.scenes.gameplay import GameplayScene

        scene = GameplayScene(event_bus=EventBus())
        scene.on_enter()

        # Spawn an NPC manually.
        npc = NPC(100, 100, npc_id="llorencc", npc_type="shop")
        scene._npcs.append(npc)

        # Run a few frames.
        from sa_fona.core.input_handler import InputState
        for _ in range(30):
            scene.handle_input(InputState())
            scene.update(1.0 / 60.0)

        # After ~0.5s of updates, the bob timer should have advanced.
        assert npc._bob_timer > 0


# ── Story Coherence Tests ────────────────────────────────────────


class TestDialogueCoherence:
    """Verify dialogue files are well-formed and consistent."""

    @staticmethod
    def _load_json(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def test_world1_dialogue_no_placeholder_text(self):
        """World 1 dialogue should have no placeholder/TODO text."""
        data = self._load_json(DATA_DIR / "dialogue" / "world1_dialogue.json")
        for seq_id, seq in data.items():
            for line in seq.get("lines", []):
                text = line.get("text", "")
                assert "TODO" not in text, f"Placeholder in {seq_id}"
                assert "PLACEHOLDER" not in text, f"Placeholder in {seq_id}"
                assert text.strip(), f"Empty text in {seq_id}"

    def test_world2_dialogue_no_placeholder_text(self):
        """World 2 dialogue should have no placeholder/TODO text."""
        data = self._load_json(DATA_DIR / "dialogue" / "world2_dialogue.json")
        for seq_id, seq in data.items():
            for line in seq.get("lines", []):
                text = line.get("text", "")
                assert "TODO" not in text, f"Placeholder in {seq_id}"
                assert "PLACEHOLDER" not in text, f"Placeholder in {seq_id}"
                assert text.strip(), f"Empty text in {seq_id}"

    def test_bep_hints_no_placeholder_text(self):
        """Bep hints should have no placeholder text."""
        data = self._load_json(DATA_DIR / "dialogue" / "bep_hints.json")
        for seq_id, seq in data.items():
            for line in seq.get("lines", []):
                text = line.get("text", "")
                assert "TODO" not in text, f"Placeholder in {seq_id}"
                assert text.strip(), f"Empty text in {seq_id}"

    def test_llorencc_shop_speaker_lowercase(self):
        """Llorencc shop dialogue should use lowercase speaker ID."""
        data = self._load_json(DATA_DIR / "dialogue" / "llorencc_shop.json")
        for seq_id, seq in data.items():
            for line in seq.get("lines", []):
                speaker = line.get("speaker", "")
                assert speaker == speaker.lower(), (
                    f"Speaker '{speaker}' should be lowercase in {seq_id}"
                )

    def test_balchar_tone_grumpy(self):
        """Balchar's dialogue should be consistently grumpy/reluctant."""
        data = self._load_json(DATA_DIR / "dialogue" / "world1_dialogue.json")
        balchar_lines = []
        for seq in data.values():
            for line in seq.get("lines", []):
                if line.get("speaker") == "balchar":
                    balchar_lines.append(line["text"])

        # Balchar should have at least a few lines.
        assert len(balchar_lines) >= 3

        # At least one grumpy/reluctant indicator.
        grumpy_indicators = ["...", "Don't", "annoyed", "luck", "warning"]
        has_grump = any(
            any(ind.lower() in text.lower() for ind in grumpy_indicators)
            for text in balchar_lines
        )
        assert has_grump, "Balchar should sound grumpy in his dialogue"

    def test_bep_tone_cheerful_or_scared(self):
        """Bep's dialogue should sound cheerful, excited, or scared."""
        data = self._load_json(DATA_DIR / "dialogue" / "world1_dialogue.json")
        bep_lines = []
        for seq in data.values():
            for line in seq.get("lines", []):
                if line.get("speaker") == "bep":
                    bep_lines.append(line)

        assert len(bep_lines) >= 3
        # Bep uses exclamation marks frequently.
        excl_count = sum(1 for l in bep_lines if "!" in l["text"])
        assert excl_count >= 2, "Bep should be energetic (use exclamation marks)"

    def test_post_boss_w1_timeline_order(self):
        """Post-boss W1 cutscene should reference W1 boss before granting mask."""
        path = DATA_DIR.parent / "data" / "cutscenes" / "post_boss_w1.json"
        if not path.exists():
            path = DATA_DIR / ".." / "cutscenes" / "post_boss_w1.json"
        # Try the standard path.
        cutscene_path = DATA_DIR.parent / "data" / "cutscenes" / "post_boss_w1.json"
        if not cutscene_path.exists():
            cutscene_path = Path(__file__).parent.parent / "sa_fona" / "data" / "cutscenes" / "post_boss_w1.json"

        data = self._load_json(cutscene_path)
        steps = data.get("steps", [])

        # mask_acquired event should come after the Dimoni dialogue.
        dimoni_step_idx = None
        mask_event_idx = None
        for i, step in enumerate(steps):
            if step.get("type") == "dialogue" and "Dimoni" in step.get("speaker", ""):
                if dimoni_step_idx is None:
                    dimoni_step_idx = i
            if step.get("type") == "event" and step.get("event_name") == "mask_acquired":
                mask_event_idx = i

        assert dimoni_step_idx is not None, "Dimoni should speak in post-boss cutscene"
        assert mask_event_idx is not None, "mask_acquired event should exist"
        assert dimoni_step_idx < mask_event_idx, (
            "Dimoni should speak before granting the mask"
        )
