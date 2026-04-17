"""Test scene for proof-of-life demonstration of the engine stack."""

from __future__ import annotations

import pygame

from sa_fona.core.input_handler import InputState
from sa_fona.scenes.base_scene import BaseScene

# Ramon placeholder dimensions and color.
_RAMON_WIDTH = 24
_RAMON_HEIGHT = 32
_RAMON_COLOR = (50, 100, 200)

# Movement speed in pixels per second.
_MOVE_SPEED = 150.0

# UI text.
_TITLE_TEXT = "Sa Fona - Test Scene"
_TITLE_COLOR = (255, 255, 255)
_TITLE_MARGIN_TOP = 10


class TestScene(BaseScene):
    """Proof-of-life scene with a movable blue rectangle.

    Displays a blue rectangle representing Ramon at the center of the
    screen. The rectangle moves with arrow keys / WASD input. Pressing
    ESC (pause_pressed) sets the quit_requested flag.
    """

    def __init__(self, screen_width: int = 384, screen_height: int = 216) -> None:
        """Initialize the test scene.

        Args:
            screen_width: Width of the game surface in pixels.
            screen_height: Height of the game surface in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height

        # Ramon position (center of screen).
        self._x = float((screen_width - _RAMON_WIDTH) // 2)
        self._y = float((screen_height - _RAMON_HEIGHT) // 2)

        # Velocity components for this frame.
        self._vx = 0.0
        self._vy = 0.0

        self.quit_requested = False

        self._font: pygame.font.Font | None = None
        self._title_surface: pygame.Surface | None = None
        self._ramon_surface: pygame.Surface | None = None

    def on_enter(self) -> None:
        """Initialize font and pre-render static surfaces."""
        pygame.font.init()
        self._font = pygame.font.Font(None, 16)
        self._title_surface = self._font.render(
            _TITLE_TEXT, True, _TITLE_COLOR
        )
        self._ramon_surface = pygame.Surface((_RAMON_WIDTH, _RAMON_HEIGHT))
        self._ramon_surface.fill(_RAMON_COLOR)

    def handle_input(self, input_state: InputState) -> None:
        """Process input to set velocity and check for quit.

        Args:
            input_state: The current frame's input snapshot.
        """
        self._vx = input_state.move_x * _MOVE_SPEED

        if input_state.jump_pressed or input_state.jump_held:
            self._vy = -_MOVE_SPEED
        else:
            self._vy = 0.0

        if input_state.pause_pressed:
            self.quit_requested = True

    def update(self, dt: float) -> None:
        """Update Ramon's position based on velocity and delta time.

        Args:
            dt: Seconds since the last frame.
        """
        self._x += self._vx * dt
        self._y += self._vy * dt

        # Clamp to screen bounds.
        self._x = max(0.0, min(self._x, self._screen_width - _RAMON_WIDTH))
        self._y = max(0.0, min(self._y, self._screen_height - _RAMON_HEIGHT))

    def render(self, surface: pygame.Surface) -> None:
        """Render the title text and Ramon rectangle.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill((20, 20, 40))

        # Draw title centered at top.
        if self._title_surface is not None:
            title_x = (self._screen_width - self._title_surface.get_width()) // 2
            surface.blit(self._title_surface, (title_x, _TITLE_MARGIN_TOP))

        # Draw Ramon placeholder.
        if self._ramon_surface is not None:
            surface.blit(self._ramon_surface, (int(self._x), int(self._y)))
