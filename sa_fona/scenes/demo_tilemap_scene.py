"""Demo scene showcasing tilemap, physics, and camera systems."""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH, DATA_DIR
from sa_fona.core.camera import Camera
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.physics import PhysicsSystem

# Ramon placeholder dimensions and color.
_RAMON_WIDTH = 24
_RAMON_HEIGHT = 32
_RAMON_COLOR = (50, 100, 200)

# Movement parameters.
_MOVE_SPEED = 150.0  # px/s horizontal
_JUMP_VELOCITY = -320.0  # px/s upward impulse

# Screen shake test parameters.
_SHAKE_INTENSITY = 6.0
_SHAKE_DURATION = 0.3


class DemoTilemapScene(BaseScene):
    """Demo scene with tilemap, physics, and camera.

    Loads the test level, creates a physics system and camera, and
    lets the player control a blue rectangle affected by gravity.

    Controls:
        - Arrow keys / WASD: move left/right
        - Space / W / Up: jump
        - Enter (interact): trigger screen shake
        - ESC: quit
    """

    def __init__(
        self,
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
        event_bus: EventBus | None = None,
        level_path: str | None = None,
    ) -> None:
        """Initialise the demo scene.

        Args:
            screen_width: Width of the game surface in pixels.
            screen_height: Height of the game surface in pixels.
            event_bus: Optional event bus for screen shake events.
            level_path: Path to the level JSON. Defaults to the test level.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height

        # Load level.
        if level_path is None:
            level_path = str(DATA_DIR / "levels" / "test" / "test_level.json")
        loader = LevelLoader()
        self._level_data = loader.load(level_path)
        self._tilemap = self._level_data.tilemap

        # Physics.
        self._physics = PhysicsSystem(self._tilemap)

        # Camera.
        self._camera = Camera(
            self._tilemap.width_pixels,
            self._tilemap.height_pixels,
            screen_width,
            screen_height,
        )

        # Player rect (spawn position from level data, in pixels).
        spawn_x = self._level_data.player_spawn[0] * TILE_SIZE
        spawn_y = self._level_data.player_spawn[1] * TILE_SIZE
        self._player_rect = pygame.Rect(
            spawn_x, spawn_y, _RAMON_WIDTH, _RAMON_HEIGHT
        )
        self._velocity: list[float] = [0.0, 0.0]
        self._on_ground: bool = False

        # Input state cache.
        self._move_x: float = 0.0
        self._jump_pressed: bool = False
        self._interact_pressed: bool = False

        self.quit_requested: bool = False

        # EventBus for screen shake.
        self._event_bus = event_bus or EventBus()
        self._event_bus.subscribe("screen_shake", self._on_screen_shake)

        self._ramon_surface: pygame.Surface | None = None

    def on_enter(self) -> None:
        """Pre-render the Ramon placeholder surface."""
        self._ramon_surface = pygame.Surface((_RAMON_WIDTH, _RAMON_HEIGHT))
        self._ramon_surface.fill(_RAMON_COLOR)

    def handle_input(self, input_state: InputState) -> None:
        """Process input for movement, jumping, shake, and quit.

        Args:
            input_state: The current frame's input snapshot.
        """
        self._move_x = input_state.move_x
        self._jump_pressed = input_state.jump_pressed
        self._interact_pressed = input_state.interact_pressed

        if input_state.pause_pressed:
            self.quit_requested = True

    def update(self, dt: float) -> None:
        """Update physics, camera, and handle interactions.

        Args:
            dt: Seconds since the last frame.
        """
        # Horizontal movement.
        self._velocity[0] = self._move_x * _MOVE_SPEED

        # Jump (only when on ground).
        if self._jump_pressed and self._on_ground:
            self._velocity[1] = _JUMP_VELOCITY

        # Physics step.
        self._player_rect, self._velocity, self._on_ground = (
            self._physics.update_rect(
                self._player_rect, self._velocity, dt, self._on_ground
            )
        )

        # Screen shake on interact.
        if self._interact_pressed:
            self._event_bus.publish(
                "screen_shake",
                intensity=_SHAKE_INTENSITY,
                duration=_SHAKE_DURATION,
            )

        # Camera follow and update.
        self._camera.follow(self._player_rect, dt)
        self._camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Render tilemap layers and the player.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill((30, 30, 50))

        cam_offset = self._camera.offset

        # Render tilemap layers back-to-front.
        self._tilemap.render_layer(surface, "background", cam_offset)
        self._tilemap.render_layer(surface, "midground", cam_offset)

        # Draw player.
        if self._ramon_surface is not None:
            screen_rect = self._camera.apply(self._player_rect)
            surface.blit(self._ramon_surface, (screen_rect.x, screen_rect.y))

        # Foreground layer on top.
        self._tilemap.render_layer(surface, "foreground", cam_offset)

    # ── Event callbacks ────────────────────────────────────────────

    def _on_screen_shake(self, intensity: float = 0.0, duration: float = 0.0) -> None:
        """Handle screen_shake events from the EventBus.

        Args:
            intensity: Shake intensity in pixels.
            duration: Shake duration in seconds.
        """
        self._camera.shake(intensity, duration)
