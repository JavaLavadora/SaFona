"""Tests for the HUD (heads-up display)."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.ui.hud import HUD


@pytest.fixture
def bus():
    """Create a fresh EventBus."""
    return EventBus()


@pytest.fixture
def hud(bus):
    """Create a HUD with default settings."""
    return HUD(bus, max_hearts=3, current_hearts=3.0, stone_count=0)


class TestHUDInit:
    """Tests for HUD initialization."""

    def test_default_max_hearts(self, hud):
        assert hud.max_hearts == 3

    def test_default_current_hearts(self, hud):
        assert hud.current_hearts == 3.0

    def test_default_stone_count(self, hud):
        assert hud.stone_count == 0

    def test_custom_init(self, bus):
        h = HUD(bus, max_hearts=5, current_hearts=4.5, stone_count=10)
        assert h.max_hearts == 5
        assert h.current_hearts == 4.5
        assert h.stone_count == 10


class TestHUDDataUpdate:
    """Tests for HUD data updates via events and direct set."""

    def test_heart_collected_increases_hearts(self, bus, hud):
        hud.current_hearts = 1.0
        bus.publish("heart_collected", amount=1.0)
        assert hud.current_hearts == 2.0

    def test_heart_collected_capped_at_max(self, bus, hud):
        hud.current_hearts = 3.0
        bus.publish("heart_collected", amount=1.0)
        assert hud.current_hearts == 3.0

    def test_half_heart_collection(self, bus, hud):
        hud.current_hearts = 2.5
        bus.publish("heart_collected", amount=0.5)
        assert hud.current_hearts == 3.0

    def test_stone_collected_increases_count(self, bus, hud):
        bus.publish("stone_collected", amount=5)
        assert hud.stone_count == 5

    def test_stone_collected_accumulates(self, bus, hud):
        bus.publish("stone_collected", amount=3)
        bus.publish("stone_collected", amount=2)
        assert hud.stone_count == 5

    def test_damage_taken_decreases_hearts(self, bus, hud):
        hud.current_hearts = 3.0
        bus.publish("damage_taken", amount=1.0)
        assert hud.current_hearts == 2.0

    def test_damage_taken_half_heart(self, bus, hud):
        hud.current_hearts = 3.0
        bus.publish("damage_taken", amount=0.5)
        assert hud.current_hearts == 2.5

    def test_damage_taken_clamped_at_zero(self, bus, hud):
        hud.current_hearts = 0.5
        bus.publish("damage_taken", amount=2.0)
        assert hud.current_hearts == 0.0

    def test_set_state(self, hud):
        hud.set_state(max_hearts=5, current_hearts=4.0, stone_count=99)
        assert hud.max_hearts == 5
        assert hud.current_hearts == 4.0
        assert hud.stone_count == 99

    def test_set_state_partial(self, hud):
        hud.set_state(stone_count=50)
        assert hud.max_hearts == 3  # unchanged
        assert hud.stone_count == 50

    def test_set_state_clamps_hearts(self, hud):
        hud.set_state(max_hearts=3, current_hearts=10.0)
        assert hud.current_hearts == 3.0

    def test_set_stone_count_negative_clamped(self, hud):
        hud.stone_count = -5
        assert hud.stone_count == 0


class TestHUDRender:
    """Tests for HUD rendering (should not crash)."""

    def test_render_does_not_crash(self, hud):
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        hud.render(surface)

    def test_render_with_zero_hearts(self, hud):
        hud.current_hearts = 0.0
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        hud.render(surface)

    def test_render_with_half_hearts(self, hud):
        hud.current_hearts = 1.5
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        hud.render(surface)

    def test_render_with_many_stones(self, hud):
        hud.stone_count = 9999
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        hud.render(surface)


class TestHUDCleanup:
    """Tests for HUD EventBus cleanup."""

    def test_cleanup_unsubscribes(self, bus, hud):
        hud.cleanup()
        # After cleanup, events should not affect the HUD.
        hud.current_hearts = 2.0
        bus.publish("heart_collected", amount=1.0)
        assert hud.current_hearts == 2.0  # unchanged
