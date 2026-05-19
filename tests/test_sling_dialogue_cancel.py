"""Tests for sling cancellation when dialogue starts (Issue #102).

Verifies that the SlingSystem.cancel() method resets the sling to idle,
and that GameplayScene._push_dialogue() calls it so the sling doesn't
get stuck in 'charging' while a dialogue overlay is active.
"""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import Player
from sa_fona.scenes.gameplay import GameplayScene
from sa_fona.systems.sling_system import SlingSystem


# Minimal economy data matching economy.json structure.
ECONOMY_DATA = {
    "sling": {
        "charge_thresholds": {
            "tier_1": {"min_hold": 0.3, "damage_multiplier": 1.0, "range_tiles": 8},
            "tier_2": {"min_hold": 0.8, "damage_multiplier": 2.0, "range_tiles": 15},
            "tier_3": {"min_hold": 1.5, "damage_multiplier": 3.0, "range_tiles": 24},
        },
        "tap_damage": 1.0,
        "projectile_speed": 250.0,
        "tap_hitbox_width": 28,
        "tap_hitbox_height": 20,
        "tap_duration": 0.1,
        "projectile_width": 8,
        "projectile_height": 8,
    }
}


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def sling(event_bus: EventBus) -> SlingSystem:
    return SlingSystem(event_bus, ECONOMY_DATA)


@pytest.fixture
def player() -> Player:
    return Player(100.0, 100.0)


def _charge_sling(sling: SlingSystem, player: Player, hold_frames: int = 24) -> None:
    """Press and hold attack to enter charging state."""
    sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
    for _ in range(hold_frames - 1):
        sling.update(InputState(attack_held=True), player, 1 / 60)


class TestSlingCancel:
    """Tests for SlingSystem.cancel()."""

    def test_cancel_from_charging_resets_to_idle(
        self, sling: SlingSystem, player: Player,
    ) -> None:
        """Cancelling while charging should return to idle."""
        _charge_sling(sling, player)
        assert sling.state == "charging"

        sling.cancel()

        assert sling.state == "idle"

    def test_cancel_resets_charge_tier(
        self, sling: SlingSystem, player: Player,
    ) -> None:
        """Cancelling should reset the charge tier to 0."""
        _charge_sling(sling, player)
        assert sling.charge_tier >= 1

        sling.cancel()

        assert sling.charge_tier == 0

    def test_cancel_resets_charge_time(
        self, sling: SlingSystem, player: Player,
    ) -> None:
        """Cancelling should reset the charge time to 0."""
        _charge_sling(sling, player)
        assert sling.charge_time > 0

        sling.cancel()

        assert sling.charge_time == 0.0

    def test_cancel_from_pressed_state(
        self, sling: SlingSystem, player: Player,
    ) -> None:
        """Cancelling from 'pressed' state should also reset to idle."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        assert sling.state == "pressed"

        sling.cancel()

        assert sling.state == "idle"

    def test_cancel_from_idle_is_noop(self, sling: SlingSystem) -> None:
        """Cancelling from idle should remain idle (no crash)."""
        assert sling.state == "idle"
        sling.cancel()
        assert sling.state == "idle"

    def test_sling_works_normally_after_cancel(
        self, sling: SlingSystem, player: Player,
    ) -> None:
        """After cancel, the sling should accept new input normally."""
        _charge_sling(sling, player)
        sling.cancel()

        # Start a new charge cycle and release to fire a projectile.
        _charge_sling(sling, player)
        assert sling.state == "charging"
        assert sling.charge_tier >= 1

        projectiles = sling.update(
            InputState(attack_released=True), player, 1 / 60,
        )
        assert len(projectiles) == 1
        assert sling.state == "cooldown"


class TestDialogueCancelsSling:
    """Integration tests: dialogue push cancels in-progress sling charge."""

    @pytest.fixture
    def scene(self) -> GameplayScene:
        return GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())

    def _settle_scene(self, scene: GameplayScene, frames: int = 30) -> None:
        """Run a few idle frames so the player lands on ground."""
        empty = InputState()
        for _ in range(frames):
            scene.handle_input(empty)
            scene.update(1 / 60)

    def test_dialogue_resets_sling_to_idle(self, scene: GameplayScene) -> None:
        """When dialogue triggers during charging, sling resets to idle."""
        self._settle_scene(scene)

        # Start charging the sling.
        attack_press = InputState(attack_pressed=True, attack_held=True)
        scene.handle_input(attack_press)
        scene.update(1 / 60)
        for _ in range(20):
            scene.handle_input(InputState(attack_held=True))
            scene.update(1 / 60)

        assert scene.sling_system.state == "charging"

        # Simulate a dialogue trigger by setting the pending dialogue
        # ID and running an update. _push_dialogue is called which
        # should cancel the sling.  We need a scene_manager for push
        # to execute, so use a minimal mock.
        class _FakeSceneManager:
            def push(self, s):
                pass

        scene.scene_manager = _FakeSceneManager()
        scene._pending_dialogue_id = "test_dialogue"

        # Run update -- this processes the pending dialogue.
        scene.handle_input(InputState())
        scene.update(1 / 60)

        assert scene.sling_system.state == "idle"

    def test_dialogue_resets_player_sling_anim(self, scene: GameplayScene) -> None:
        """Player sling_anim_state should be 'none' after dialogue cancels sling."""
        self._settle_scene(scene)

        # Charge sling.
        scene.handle_input(InputState(attack_pressed=True, attack_held=True))
        scene.update(1 / 60)
        for _ in range(20):
            scene.handle_input(InputState(attack_held=True))
            scene.update(1 / 60)

        assert scene.player.sling_anim_state == "charging"

        class _FakeSceneManager:
            def push(self, s):
                pass

        scene.scene_manager = _FakeSceneManager()
        scene._pending_dialogue_id = "test_dialogue"
        scene.handle_input(InputState())
        scene.update(1 / 60)

        assert scene.player.sling_anim_state == "none"

    def test_sling_works_after_dialogue(self, scene: GameplayScene) -> None:
        """After dialogue ends, sling should work normally again."""
        self._settle_scene(scene)

        # Charge and cancel via dialogue.
        scene.handle_input(InputState(attack_pressed=True, attack_held=True))
        scene.update(1 / 60)
        for _ in range(20):
            scene.handle_input(InputState(attack_held=True))
            scene.update(1 / 60)

        class _FakeSceneManager:
            def push(self, s):
                pass

        scene.scene_manager = _FakeSceneManager()
        scene._pending_dialogue_id = "test_dialogue"
        scene.handle_input(InputState())
        scene.update(1 / 60)

        # Now simulate dialogue ended: sling should accept new input.
        # Do a tap attack.
        scene.handle_input(InputState(attack_pressed=True, attack_held=True))
        scene.update(1 / 60)
        scene.handle_input(InputState(attack_released=True))
        scene.update(1 / 60)

        # Should be in cooldown (tap completed successfully).
        assert scene.sling_system.state == "cooldown"
        assert len(scene.sling_system.melee_hitboxes) == 1
