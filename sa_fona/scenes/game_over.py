"""Game over scene: displayed when the player dies.

Placeholder implementation: dark red screen with "GAME OVER" text
and "Press any key to restart" prompt.  Pressing any key restarts
the game from the beginning of the current level.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.input_handler import InputState
from sa_fona.scenes.base_scene import BaseScene


# Colors.
_BG_COLOR: tuple[int, int, int] = (60, 15, 15)
_TITLE_COLOR: tuple[int, int, int] = (220, 40, 40)
_PROMPT_COLOR: tuple[int, int, int] = (180, 180, 180)


class GameOverScene(BaseScene):
    """Placeholder game over screen shown when the player dies.

    Displays "GAME OVER" and waits for any key press to signal
    a restart.

    Args:
        on_restart: Callback invoked when the player presses a key
            to restart.  The scene itself does not manage the scene
            stack -- the caller (GameplayScene) handles the transition.
    """

    def __init__(self, on_restart: callable = None) -> None:
        self._on_restart = on_restart
        self._any_key_pressed: bool = False

        # Fonts (initialized on first render).
        self._title_font: pygame.font.Font | None = None
        self._prompt_font: pygame.font.Font | None = None

        # Delay before accepting input (prevents accidental skip).
        self._input_delay: float = 0.5

    def on_enter(self) -> None:
        """Reset state on scene entry."""
        self._any_key_pressed = False
        self._input_delay = 0.5

    def handle_input(self, input_state: InputState) -> None:
        """Check for any key press to restart.

        Args:
            input_state: Current frame's input snapshot.
        """
        if self._input_delay > 0:
            return

        # Check if any action is pressed.
        any_pressed = (
            input_state.jump_pressed
            or input_state.attack_pressed
            or input_state.interact_pressed
            or input_state.pause_pressed
            or input_state.reset_pressed
        )
        if any_pressed:
            self._any_key_pressed = True

    def update(self, dt: float) -> None:
        """Tick the input delay and handle restart.

        Args:
            dt: Delta time in seconds.
        """
        if self._input_delay > 0:
            self._input_delay -= dt

        if self._any_key_pressed and self._on_restart is not None:
            self._on_restart()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the game over screen.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill(_BG_COLOR)

        # Initialize fonts lazily.
        if self._title_font is None:
            try:
                self._title_font = pygame.font.Font(None, 32)
            except Exception:
                self._title_font = None

        if self._prompt_font is None:
            try:
                self._prompt_font = pygame.font.Font(None, 16)
            except Exception:
                self._prompt_font = None

        # "GAME OVER" title.
        if self._title_font is not None:
            title = self._title_font.render("GAME OVER", False, _TITLE_COLOR)
            tx = (surface.get_width() - title.get_width()) // 2
            ty = surface.get_height() // 3
            surface.blit(title, (tx, ty))

        # "Press any key to restart" prompt.
        if self._prompt_font is not None and self._input_delay <= 0:
            prompt = self._prompt_font.render(
                "Press any key to restart", False, _PROMPT_COLOR
            )
            px = (surface.get_width() - prompt.get_width()) // 2
            py = surface.get_height() * 2 // 3
            surface.blit(prompt, (px, py))
