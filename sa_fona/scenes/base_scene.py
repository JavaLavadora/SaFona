"""Abstract base class for all game scenes."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from sa_fona.core.input_handler import InputState


class BaseScene(ABC):
    """Abstract base class for all game scenes.

    Scenes implement lifecycle hooks (on_enter, on_exit, on_resume) and the
    per-frame handle_input / update / render methods. The SceneManager calls
    these at the appropriate times.
    """

    def on_enter(self) -> None:
        """Called when this scene becomes active (pushed or replaced onto stack)."""

    def on_exit(self) -> None:
        """Called when this scene is removed from the stack."""

    def on_resume(self) -> None:
        """Called when the scene above is popped, making this scene active again."""

    @abstractmethod
    def handle_input(self, input_state: InputState) -> None:
        """Process the current frame's input state.

        Args:
            input_state: Snapshot of all logical input actions for this frame.
        """

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene logic.

        Args:
            dt: Delta time in seconds since the last frame.
        """

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the scene to the given surface.

        Args:
            surface: The pygame Surface to draw on.
        """

    @property
    def is_overlay(self) -> bool:
        """If True, the scene below this one is also rendered (dimmed).

        Returns:
            False by default. Override in subclasses for overlay scenes
            like pause menus.
        """
        return False
