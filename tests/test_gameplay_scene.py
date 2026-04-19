"""Tests for the GameplayScene."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import PlayerState
from sa_fona.scenes.gameplay import (
    BG_DIM_ALPHA,
    PARALLAX_FACTOR_INTERIOR,
    PARALLAX_FACTOR_OUTDOOR,
    GameplayScene,
)


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


class TestGameplaySceneReset:
    """Tests for the R key level reset."""

    def test_reset_respawns_player_at_spawn(self, scene: GameplayScene) -> None:
        """Pressing reset should move the player back to the spawn point."""
        scene.on_enter()

        # Record initial spawn position.
        initial_x = scene.player.rect.x
        initial_y = scene.player.rect.y

        # Move the player around.
        for _ in range(30):
            scene.handle_input(InputState(move_right=True, move_x=1.0))
            scene.update(1.0 / 60.0)

        assert scene.player.rect.x != initial_x, "Player should have moved"

        # Press reset.
        scene.handle_input(InputState(reset_pressed=True))

        # Player should be back at spawn.
        assert scene.player.rect.x == initial_x
        assert scene.player.rect.y == initial_y

    def test_reset_clears_player_velocity(self, scene: GameplayScene) -> None:
        """After reset, the player should have zero velocity."""
        scene.on_enter()

        # Give the player some velocity.
        scene.handle_input(InputState(jump_pressed=True, jump_held=True))
        scene.update(1.0 / 60.0)
        assert scene.player.velocity[1] != 0.0

        # Reset.
        scene.handle_input(InputState(reset_pressed=True))
        assert scene.player.velocity == [0.0, 0.0]

    def test_reset_creates_fresh_player(self, scene: GameplayScene) -> None:
        """After reset, the player should be in IDLE state."""
        scene.on_enter()

        # Jump to change state.
        empty = InputState()
        for _ in range(30):
            scene.handle_input(empty)
            scene.update(1.0 / 60.0)
        scene.handle_input(InputState(jump_pressed=True, jump_held=True))
        scene.update(1.0 / 60.0)
        assert scene.player.state != PlayerState.IDLE

        # Reset.
        scene.handle_input(InputState(reset_pressed=True))
        assert scene.player.state == PlayerState.IDLE


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


class TestSlingAnimationStateSync:
    """Tests for sling animation state mapping from SlingSystem to player."""

    def test_idle_maps_to_none(self, scene: GameplayScene) -> None:
        """SlingSystem 'idle' state maps to player sling_anim_state 'none'."""
        scene.on_enter()
        scene._sling_system._state = "idle"
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        assert scene.player.sling_anim_state == "none"

    def test_pressed_maps_to_charging(self, scene: GameplayScene) -> None:
        """SlingSystem 'pressed' state maps to player sling_anim_state 'charging'."""
        scene.on_enter()
        scene._sling_system._state = "pressed"
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        assert scene.player.sling_anim_state == "charging"

    def test_charging_maps_to_charging(self, scene: GameplayScene) -> None:
        """SlingSystem 'charging' state maps to player sling_anim_state 'charging'."""
        scene.on_enter()
        scene._sling_system._state = "charging"
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        assert scene.player.sling_anim_state == "charging"

    def test_cooldown_maps_to_releasing(self, scene: GameplayScene) -> None:
        """SlingSystem 'cooldown' maps to 'releasing' unconditionally."""
        scene.on_enter()
        scene._sling_system._state = "cooldown"
        # Set a non-zero cooldown timer so it doesn't expire in one tick.
        scene._sling_system._cooldown_timer = 0.15
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        assert scene.player.sling_anim_state == "releasing"


class TestParallaxAndDimming:
    """Tests for parallax scrolling and background dimming."""

    def test_parallax_constants_are_sensible(self) -> None:
        """Parallax factors should be between 0 and 1."""
        assert 0.0 < PARALLAX_FACTOR_OUTDOOR < 1.0
        assert 0.0 < PARALLAX_FACTOR_INTERIOR < 1.0
        assert PARALLAX_FACTOR_OUTDOOR > PARALLAX_FACTOR_INTERIOR

    def test_dim_alpha_is_sensible(self) -> None:
        """Dim alpha should be between 0 (transparent) and 255 (opaque)."""
        assert 0 < BG_DIM_ALPHA < 255

    def test_interior_level_detection(self) -> None:
        """Test level is not interior (test level has no cave/talayot tileset)."""
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())
        # Test level has no tileset metadata, so it should not be interior.
        assert scene._is_interior_level() is False

    def test_parallax_factor_for_test_level(self) -> None:
        """Test level (outdoor) should use the outdoor parallax factor."""
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())
        assert scene._get_parallax_factor() == PARALLAX_FACTOR_OUTDOOR

    def test_render_sky_with_no_background_does_not_crash(self, scene: GameplayScene) -> None:
        """Rendering the sky without a background image should not crash."""
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        scene._render_sky(surface)

    def test_render_sky_applies_dimming(self, scene: GameplayScene) -> None:
        """After _render_sky, the dim cache should be created."""
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        scene._render_sky(surface)
        assert hasattr(scene, "_dim_cache")
        assert scene._dim_cache.get_size() == (BASE_WIDTH, BASE_HEIGHT)

    def test_reset_invalidates_dim_cache(self, scene: GameplayScene) -> None:
        """After level reset, the dim cache should be cleared."""
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        scene._render_sky(surface)
        assert hasattr(scene, "_dim_cache")
        scene._reset_level()
        assert not hasattr(scene, "_dim_cache")
