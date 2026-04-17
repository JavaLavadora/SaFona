"""Scene stack manager with lifecycle management."""

from __future__ import annotations

import pygame

from sa_fona.scenes.base_scene import BaseScene


class SceneManager:
    """Push/pop scene stack with lifecycle management.

    The active scene is at the top of the stack. Pushed scenes overlay
    without destroying the scene below. Popping returns to the previous
    scene. Overlay scenes cause the scene below to also be rendered.
    """

    def __init__(self) -> None:
        """Initialize the scene manager with an empty stack."""
        self._stack: list[BaseScene] = []

    def push(self, scene: BaseScene) -> None:
        """Push a scene onto the stack and call its on_enter hook.

        Args:
            scene: The scene to push.
        """
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> None:
        """Pop the top scene, calling on_exit.

        After popping, calls on_resume on the new top scene if one exists.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._stack:
            raise IndexError("Cannot pop from an empty scene stack")
        old = self._stack.pop()
        old.on_exit()
        if self._stack:
            self._stack[-1].on_resume()

    def replace(self, scene: BaseScene) -> None:
        """Replace the top scene. Calls on_exit on old, on_enter on new.

        Args:
            scene: The scene to replace the current top with.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._stack:
            raise IndexError("Cannot replace on an empty scene stack")
        old = self._stack.pop()
        old.on_exit()
        self._stack.append(scene)
        scene.on_enter()

    def update(self, dt: float) -> None:
        """Update the active (top) scene.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        if self._stack:
            self._stack[-1].update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Render the scene stack.

        If the top scene is an overlay, the scene below it is also rendered.
        A semi-transparent dimming layer is drawn between them.

        Args:
            surface: The pygame Surface to render onto.
        """
        if not self._stack:
            return

        top = self._stack[-1]

        if top.is_overlay and len(self._stack) >= 2:
            # Render the scene below the overlay.
            self._stack[-2].render(surface)
            # Draw a semi-transparent dimming layer.
            dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 128))
            surface.blit(dim, (0, 0))

        top.render(surface)

    @property
    def active_scene(self) -> BaseScene:
        """Return the currently active (top) scene.

        Returns:
            The scene at the top of the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._stack:
            raise IndexError("No active scene — stack is empty")
        return self._stack[-1]

    @property
    def is_empty(self) -> bool:
        """Check whether the scene stack is empty.

        Returns:
            True if there are no scenes on the stack.
        """
        return len(self._stack) == 0
