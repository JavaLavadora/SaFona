"""Tests for the SlingSystem: tap detection, charge tiers, and projectile spawning."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import Player
from sa_fona.systems.sling_system import SlingSystem


# Minimal economy data matching the structure in economy.json.
ECONOMY_DATA = {
    "sling": {
        "charge_thresholds": {
            "tier_1": {"min_hold": 0.3, "max_hold": 0.8, "damage_multiplier": 1.0, "range_tiles": 8},
            "tier_2": {"min_hold": 0.8, "max_hold": 1.5, "damage_multiplier": 2.0, "range_tiles": 15},
            "tier_3": {"min_hold": 1.5, "damage_multiplier": 3.0, "range_tiles": 24},
        },
        "tap_damage": 1.0,
        "tap_range_tiles": 1.5,
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


class TestSlingSystemInit:
    """Tests for SlingSystem initialization."""

    def test_starts_idle(self, sling: SlingSystem) -> None:
        assert sling.state == "idle"

    def test_starts_not_charging(self, sling: SlingSystem) -> None:
        assert sling.is_charging is False

    def test_starts_at_tier_zero(self, sling: SlingSystem) -> None:
        assert sling.charge_tier == 0

    def test_no_melee_hitboxes(self, sling: SlingSystem) -> None:
        assert len(sling.melee_hitboxes) == 0


class TestTapDetection:
    """Tests for tap (melee) attack detection."""

    def test_tap_creates_melee_hitbox(self, sling: SlingSystem, player: Player) -> None:
        """Press and release within tap threshold creates a melee hitbox."""
        # Frame 1: press attack.
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        # Frame 2: release immediately.
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(sling.melee_hitboxes) == 1

    def test_tap_hitbox_in_front_of_player_facing_right(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Melee hitbox should appear to the right of a right-facing player."""
        player.facing_right = True
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        hitbox = sling.melee_hitboxes[0]
        assert hitbox.rect.left >= player.rect.right

    def test_tap_hitbox_in_front_of_player_facing_left(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Melee hitbox should appear to the left of a left-facing player."""
        player.facing_right = False
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        hitbox = sling.melee_hitboxes[0]
        assert hitbox.rect.right <= player.rect.left

    def test_tap_hitbox_damage(self, sling: SlingSystem, player: Player) -> None:
        """Melee hitbox should have the configured tap damage."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert sling.melee_hitboxes[0].damage == 1.0

    def test_tap_hitbox_expires(self, sling: SlingSystem, player: Player) -> None:
        """Melee hitbox should disappear after its duration."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(sling.melee_hitboxes) == 1
        # Wait for hitbox to expire (tap_duration is 0.1s).
        for _ in range(10):
            sling.update(InputState(), player, 1 / 60)
        assert len(sling.melee_hitboxes) == 0

    def test_tap_publishes_event(self, event_bus: EventBus, player: Player) -> None:
        """Tap attack should publish a sling_tap event."""
        sling = SlingSystem(event_bus, ECONOMY_DATA)
        events_received = []
        event_bus.subscribe("sling_tap", lambda **kw: events_received.append(kw))
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(events_received) == 1
        assert events_received[0]["damage"] == 1.0

    def test_tap_returns_no_projectile(self, sling: SlingSystem, player: Player) -> None:
        """Tap should not spawn a projectile."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        result = sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(result) == 0


class TestCharging:
    """Tests for charge state transitions and tier detection."""

    def test_holding_past_tap_threshold_enters_charging(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Holding attack past the tap threshold transitions to charging."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        # Hold for 200ms (past 120ms tap threshold).
        for _ in range(12):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        assert sling.is_charging

    def test_tier_1_reached_at_300ms(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Charge tier 1 is reached at 0.3s hold time."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        # Hold for ~0.32s total (20 frames at 60 FPS).
        for _ in range(19):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        assert sling.charge_tier == 1

    def test_tier_2_reached_at_800ms(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Charge tier 2 is reached at 0.8s hold time."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        # Hold for ~0.82s total (50 frames at 60 FPS).
        for _ in range(49):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        assert sling.charge_tier == 2

    def test_tier_3_reached_at_1500ms(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Charge tier 3 is reached at 1.5s hold time."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        # Hold for ~1.52s total (92 frames at 60 FPS).
        for _ in range(91):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        assert sling.charge_tier == 3

    def test_charge_time_tracks_correctly(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Charge time should increase while holding."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        for _ in range(29):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        # ~0.5s total.
        assert 0.45 < sling.charge_time < 0.55


class TestProjectileSpawning:
    """Tests for projectile creation on charge release."""

    def _charge_and_release(
        self,
        sling: SlingSystem,
        player: Player,
        hold_frames: int,
    ) -> list:
        """Helper: press, hold for N frames, then release."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        for _ in range(hold_frames - 1):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        return sling.update(InputState(attack_released=True), player, 1 / 60)

    def test_tier1_release_creates_projectile(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Releasing at tier 1 should spawn a projectile."""
        # Hold 24 frames (~0.4s) to be well past tier 1 threshold.
        projectiles = self._charge_and_release(sling, player, 24)
        assert len(projectiles) == 1

    def test_tier2_release_creates_projectile(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Releasing at tier 2 should spawn a projectile."""
        projectiles = self._charge_and_release(sling, player, 54)
        assert len(projectiles) == 1

    def test_tier3_release_creates_projectile(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Releasing at tier 3 should spawn a projectile."""
        projectiles = self._charge_and_release(sling, player, 96)
        assert len(projectiles) == 1

    def test_projectile_direction_right(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Projectile should move right when player faces right."""
        player.facing_right = True
        projectiles = self._charge_and_release(sling, player, 24)
        assert projectiles[0].velocity[0] > 0

    def test_projectile_direction_left(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Projectile should move left when player faces left."""
        player.facing_right = False
        projectiles = self._charge_and_release(sling, player, 24)
        assert projectiles[0].velocity[0] < 0

    def test_tier1_damage(self, sling: SlingSystem, player: Player) -> None:
        """Tier 1 projectile damage should be tap_damage * 1.0."""
        projectiles = self._charge_and_release(sling, player, 24)
        assert projectiles[0].damage == pytest.approx(1.0)

    def test_tier2_damage(self, sling: SlingSystem, player: Player) -> None:
        """Tier 2 projectile damage should be tap_damage * 2.0."""
        projectiles = self._charge_and_release(sling, player, 54)
        assert projectiles[0].damage == pytest.approx(2.0)

    def test_tier3_damage(self, sling: SlingSystem, player: Player) -> None:
        """Tier 3 projectile damage should be tap_damage * 3.0."""
        projectiles = self._charge_and_release(sling, player, 96)
        assert projectiles[0].damage == pytest.approx(3.0)

    def test_projectile_charge_tier_attribute(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Projectile should store which charge tier created it."""
        projectiles = self._charge_and_release(sling, player, 54)
        assert projectiles[0].charge_tier == 2

    def test_release_publishes_event(
        self, event_bus: EventBus, player: Player
    ) -> None:
        """Releasing a charged shot should publish sling_release event."""
        sling = SlingSystem(event_bus, ECONOMY_DATA)
        events = []
        event_bus.subscribe("sling_release", lambda **kw: events.append(kw))
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        for _ in range(23):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(events) == 1
        assert events[0]["tier"] == 1

    def test_below_tier1_gives_melee_fallback(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Releasing charge below tier 1 should fire a melee tap as fallback."""
        # Hold only ~0.15s (9 frames) -- past tap threshold but below tier 1.
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        for _ in range(8):
            sling.update(InputState(attack_held=True), player, 1 / 60)
        projectiles = sling.update(InputState(attack_released=True), player, 1 / 60)
        assert len(projectiles) == 0
        assert len(sling.melee_hitboxes) == 1


class TestCooldown:
    """Tests for attack cooldown between actions."""

    def test_cooldown_after_tap(self, sling: SlingSystem, player: Player) -> None:
        """System should enter cooldown after a tap attack."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        assert sling.state == "cooldown"

    def test_cooldown_clears(self, sling: SlingSystem, player: Player) -> None:
        """Cooldown should expire and return to idle."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        # Wait out the cooldown (0.15s = 9 frames at 60 FPS).
        for _ in range(12):
            sling.update(InputState(), player, 1 / 60)
        assert sling.state == "idle"

    def test_cannot_attack_during_cooldown(
        self, sling: SlingSystem, player: Player
    ) -> None:
        """Pressing attack during cooldown should not start a new attack."""
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        sling.update(InputState(attack_released=True), player, 1 / 60)
        # Try to attack during cooldown.
        sling.update(InputState(attack_pressed=True, attack_held=True), player, 1 / 60)
        assert sling.state == "cooldown"
