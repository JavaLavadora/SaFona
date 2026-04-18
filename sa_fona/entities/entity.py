"""Base class for all game entities.

Provides position, velocity, bounding rect, and a sprite surface
reference.  Concrete entities (Player, Enemy, Projectile) extend
this with specific behaviour.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class Entity(ABC):
    """Abstract base class for all game entities.

    Attributes:
        rect: Axis-aligned bounding box in world coordinates.
        velocity: ``[vx, vy]`` in pixels per second.
        facing_right: True when the entity faces right.
        on_ground: True when the entity is resting on solid ground.
        active: False marks the entity for removal.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
    ) -> None:
        """Initialize the entity at a world position.

        Args:
            x: X position in world pixels (left edge).
            y: Y position in world pixels (top edge).
            width: Bounding box width in pixels.
            height: Bounding box height in pixels.
        """
        self.rect: pygame.Rect = pygame.Rect(int(x), int(y), width, height)
        self.velocity: list[float] = [0.0, 0.0]
        self.facing_right: bool = True
        self.on_ground: bool = False
        self.active: bool = True
        self._sprite: pygame.Surface | None = None

    # ── Properties ─────────────────────────────────────────────────

    @property
    def x(self) -> float:
        """Horizontal position (left edge) in world pixels."""
        return float(self.rect.x)

    @property
    def y(self) -> float:
        """Vertical position (top edge) in world pixels."""
        return float(self.rect.y)

    @property
    def sprite(self) -> pygame.Surface | None:
        """Current sprite surface for rendering.

        Returns:
            A pygame Surface, or None if no sprite is assigned.
        """
        return self._sprite

    @sprite.setter
    def sprite(self, surface: pygame.Surface | None) -> None:
        self._sprite = surface

    # ── Abstract interface ─────────────────────────────────────────

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance entity logic by *dt* seconds.

        Args:
            dt: Delta time in seconds since the last frame.
        """

    def render(self, surface: pygame.Surface, camera_offset: tuple[int, int]) -> None:
        """Draw the entity onto the target surface.

        The default implementation blits the current sprite at the
        camera-adjusted position.  Override for custom rendering.

        Args:
            surface: Target pygame Surface.
            camera_offset: ``(cam_x, cam_y)`` world-pixel offset of the camera.
        """
        if self._sprite is None:
            return
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        surface.blit(self._sprite, (screen_x, screen_y))
