"""Tests for the GameplayScene."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import PlayerState
from sa_fona.scenes.gameplay import GameplayScene


@pytest.fixture
def scene() -> GameplayScene:
    """Create a GameplayScene with the default test level."""
    return GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())


class TestGameplaySceneInit:
    """Tests for scene initialization."""

    def test_player_spawned(self, scene: GameplayScene) -> None:
        assert scene.player is not None

    def test_player_starts_idle_after_settling(self, scene: GameplayScene) -> None:
        scene.on_enter()
        empty = InputState()
        for _ in range(30):
            scene.handle_input(empty)
            scene.update(1.0 / 60.0)
        assert scene.player.state == PlayerState.IDLE

    def test_camera_exists(self, scene: GameplayScene) -> None:
        assert scene.camera is not None

    def test_physics_exists(self, scene: GameplayScene) -> None:
        assert scene.physics is not None


class TestGameplaySceneInput:
    """Tests for scene input handling."""

    def test_quit_on_pause(self, scene: GameplayScene) -> None:
        scene.on_enter()
        scene.handle_input(InputState(pause_pressed=True))
        assert scene.quit_requested is True

    def test_player_moves_right(self, scene: GameplayScene) -> None:
        scene.on_enter()
        empty = InputState()
        for _ in range(30):
            scene.handle_input(empty)
            scene.update(1.0 / 60.0)

        initial_x = scene.player.rect.x
        for _ in range(10):
            scene.handle_input(InputState(move_right=True, move_x=1.0))
            scene.update(1.0 / 60.0)
        assert scene.player.rect.x > initial_x


class TestGameplaySceneRender:
    """Tests for scene rendering (should not crash)."""

    def test_render_does_not_crash(self, scene: GameplayScene) -> None:
        scene.on_enter()
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        scene.render(surface)

    def test_screen_shake_via_event_bus(self) -> None:
        bus = EventBus()
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)
        scene.on_enter()
        bus.publish("screen_shake", intensity=5.0, duration=0.2)
        # Should not crash.
        scene.update(1.0 / 60.0)


class TestGameplaySceneLifecycle:
    """Tests for scene lifecycle hooks."""

    def test_on_exit_unsubscribes_event_bus(self) -> None:
        """Verify on_exit cleans up EventBus subscriptions."""
        bus = EventBus()
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=bus)
        scene.on_enter()
        # Confirm it works before exit.
        bus.publish("screen_shake", intensity=1.0, duration=0.1)

        scene.on_exit()

        # After exit, the subscriber list for screen_shake should be empty.
        assert len(bus._subscribers["screen_shake"]) == 0
