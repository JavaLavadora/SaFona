"""Tests for pit-fall death: player dies when falling below the level."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.scenes.gameplay import GameplayScene


@pytest.fixture
def scene_and_bus():
    """Create a GameplayScene with an accessible EventBus."""
    bus = EventBus()
    scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)
    scene.on_enter()
    # Settle physics for a few frames.
    empty = InputState()
    for _ in range(30):
        scene.handle_input(empty)
        scene.update(1.0 / 60.0)
    return scene, bus


class TestPitFallDeath:
    """Tests for the out-of-bounds pit-fall death mechanic."""

    def test_player_below_level_triggers_death(self, scene_and_bus) -> None:
        """Player positioned below level bounds should trigger player_died."""
        scene, bus = scene_and_bus

        death_fired = []
        bus.subscribe("player_died", lambda **kw: death_fired.append(True))

        # Move the player far below the level bottom.
        level_bottom = scene._tilemap.height_pixels
        scene._player.rect.top = level_bottom + TILE_SIZE * 2 + 1

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert len(death_fired) >= 1, "player_died should fire when below level"

    def test_player_within_level_does_not_trigger_death(
        self, scene_and_bus
    ) -> None:
        """Player within normal bounds should NOT trigger player_died."""
        scene, bus = scene_and_bus

        death_fired = []
        bus.subscribe("player_died", lambda **kw: death_fired.append(True))

        # Ensure the player is within level bounds.
        scene._player.rect.top = scene._tilemap.height_pixels - TILE_SIZE

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert len(death_fired) == 0, "player_died should not fire within bounds"

    def test_death_does_not_fire_twice(self, scene_and_bus) -> None:
        """Once pending_game_over is set, death should not fire again."""
        scene, bus = scene_and_bus

        death_count = []
        bus.subscribe("player_died", lambda **kw: death_count.append(True))

        # Move the player far below.
        level_bottom = scene._tilemap.height_pixels
        scene._player.rect.top = level_bottom + TILE_SIZE * 3

        # Run two updates — the second should NOT fire again.
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        # After the first update, _pending_game_over should be True,
        # which prevents a second publish. We need to keep the flag set
        # by NOT processing the game over (no scene manager).
        scene._pending_game_over = True
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert len(death_count) == 1, "player_died should fire only once"
