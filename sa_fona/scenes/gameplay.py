"""Gameplay scene: loads a level, spawns the player, runs physics + camera.

This scene replaces DemoTilemapScene as the default entry point for
the game.  It wires together the Player entity, PhysicsSystem, Camera,
and TileMap into a playable experience.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import (
    BASE_HEIGHT,
    BASE_WIDTH,
    DATA_DIR,
    PLAYER_GRAVITY,
)
from sa_fona.core.camera import Camera
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.player import Player
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.physics import PhysicsSystem

# Screen shake defaults.
_SHAKE_INTENSITY = 6.0
_SHAKE_DURATION = 0.3


class GameplayScene(BaseScene):
    """Playable level scene with player, physics, and camera.

    Loads a level JSON, creates a PhysicsSystem and Camera, spawns
    the Player entity (Ramon), and orchestrates per-frame updates.

    Args:
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
        event_bus: Shared event bus for cross-system communication.
        level_path: Path to the level JSON file. Defaults to the test level.
    """

    def __init__(
        self,
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
        event_bus: EventBus | None = None,
        level_path: str | None = None,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height

        # Load level.
        if level_path is None:
            level_path = str(DATA_DIR / "levels" / "test" / "test_level.json")
        loader = LevelLoader()
        self._level_data = loader.load(level_path)
        self._tilemap = self._level_data.tilemap

        # Physics.
        self._physics = PhysicsSystem(self._tilemap, gravity=PLAYER_GRAVITY)

        # Camera.
        self._camera = Camera(
            self._tilemap.width_pixels,
            self._tilemap.height_pixels,
            screen_width,
            screen_height,
        )

        # Player spawn (tile coords -> pixel coords).
        spawn_x = self._level_data.player_spawn[0] * TILE_SIZE
        spawn_y = self._level_data.player_spawn[1] * TILE_SIZE
        self._player = Player(spawn_x, spawn_y, self._physics)

        # Input state cache.
        self._input_state: InputState = InputState()
        self.quit_requested: bool = False

        # EventBus.
        self._event_bus = event_bus or EventBus()
        self._event_bus.subscribe("screen_shake", self._on_screen_shake)

    # ── Properties ─────────────────────────────────────────────────

    @property
    def player(self) -> Player:
        """The player entity (exposed for testing and future systems)."""
        return self._player

    @property
    def camera(self) -> Camera:
        """The camera (exposed for testing)."""
        return self._camera

    @property
    def physics(self) -> PhysicsSystem:
        """The physics system (exposed for testing)."""
        return self._physics

    # ── Scene lifecycle ────────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered -- nothing to set up beyond __init__."""

    def handle_input(self, input_state: InputState) -> None:
        """Forward input to the player and handle scene-level actions.

        Args:
            input_state: The current frame's input snapshot.
        """
        self._input_state = input_state
        self._player.handle_input(input_state)

        if input_state.pause_pressed:
            self.quit_requested = True

        # Debug: screen shake on interact.
        if input_state.interact_pressed:
            self._event_bus.publish(
                "screen_shake",
                intensity=_SHAKE_INTENSITY,
                duration=_SHAKE_DURATION,
            )

    def update(self, dt: float) -> None:
        """Advance simulation by one frame.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        self._player.update(dt)
        self._camera.follow(self._player.rect, dt)
        self._camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draw tilemap layers and the player.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill((30, 30, 50))
        cam_offset = self._camera.offset

        # Back-to-front layer rendering.
        self._tilemap.render_layer(surface, "background", cam_offset)
        self._tilemap.render_layer(surface, "midground", cam_offset)

        # Player.
        self._player.render(surface, cam_offset)

        # Foreground on top.
        self._tilemap.render_layer(surface, "foreground", cam_offset)

    # ── Event callbacks ────────────────────────────────────────────

    def _on_screen_shake(
        self, intensity: float = 0.0, duration: float = 0.0
    ) -> None:
        """Handle screen_shake events from the EventBus.

        Args:
            intensity: Shake intensity in pixels.
            duration: Shake duration in seconds.
        """
        self._camera.shake(intensity, duration)
