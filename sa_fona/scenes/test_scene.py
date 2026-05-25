"""Test scene for proof-of-life demonstration of the engine stack."""

from __future__ import annotations

import pygame

from sa_fona.core.input_handler import InputState
from sa_fona.config.settings import PLAYER_SPRITE_HEIGHT, PLAYER_SPRITE_WIDTH
from sa_fona.scenes.base_scene import BaseScene

# Balchar placeholder dimensions and color.
_BALCHAR_WIDTH = PLAYER_SPRITE_WIDTH
_BALCHAR_HEIGHT = PLAYER_SPRITE_HEIGHT
_BALCHAR_COLOR = (50, 100, 200)

# Movement speed in pixels per second.
_MOVE_SPEED = 150.0

# UI text.
_TITLE_TEXT = "Sa Fona - Test Scene"
_TITLE_COLOR = (255, 255, 255)
_TITLE_MARGIN_TOP = 10


class TestScene(BaseScene):
    """Proof-of-life scene with a movable blue rectangle.

    Displays a blue rectangle representing Balchar at the center of the
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

        # Balchar position (center of screen).
        self._x = float((screen_width - _BALCHAR_WIDTH) // 2)
        self._y = float((screen_height - _BALCHAR_HEIGHT) // 2)

        # Velocity components for this frame.
        self._vx = 0.0
        self._vy = 0.0

        self.quit_requested = False

        self._font: pygame.font.Font | None = None
        self._title_surface: pygame.Surface | None = None
        self._balchar_surface: pygame.Surface | None = None

    def on_enter(self) -> None:
        """Initialize font and pre-render static surfaces."""
        pygame.font.init()
        self._font = pygame.font.Font(None, 16)
        self._title_surface = self._font.render(
            _TITLE_TEXT, True, _TITLE_COLOR
        )
        self._balchar_surface = pygame.Surface((_BALCHAR_WIDTH, _BALCHAR_HEIGHT))
        self._balchar_surface.fill(_BALCHAR_COLOR)

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
        """Update Balchar's position based on velocity and delta time.

        Args:
            dt: Seconds since the last frame.
        """
        self._x += self._vx * dt
        self._y += self._vy * dt

        # Clamp to screen bounds.
        self._x = max(0.0, min(self._x, self._screen_width - _BALCHAR_WIDTH))
        self._y = max(0.0, min(self._y, self._screen_height - _BALCHAR_HEIGHT))

    def render(self, surface: pygame.Surface) -> None:
        """Render the title text and Balchar rectangle.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill((20, 20, 40))

        # Draw title centered at top.
        if self._title_surface is not None:
            title_x = (self._screen_width - self._title_surface.get_width()) // 2
            surface.blit(self._title_surface, (title_x, _TITLE_MARGIN_TOP))

        # Draw Balchar placeholder.
        if self._balchar_surface is not None:
            surface.blit(self._balchar_surface, (int(self._x), int(self._y)))
