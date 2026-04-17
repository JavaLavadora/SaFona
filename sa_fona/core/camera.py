"""Camera follow system with smooth interpolation and screen shake."""

from __future__ import annotations

import random

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH


class Camera:
    """Follows a target with smooth interpolation and screen shake.

    The camera tracks a target rectangle, smoothly centering it on
    screen via linear interpolation.  It clamps to level bounds so the
    viewport never shows outside the level, and supports a decaying
    screen-shake effect.

    Attributes:
        view_width: Viewport width in pixels.
        view_height: Viewport height in pixels.
    """

    def __init__(
        self,
        level_width: int,
        level_height: int,
        view_width: int = BASE_WIDTH,
        view_height: int = BASE_HEIGHT,
    ) -> None:
        """Initialise the camera.

        Args:
            level_width: Total level width in pixels.
            level_height: Total level height in pixels.
            view_width: Viewport width. Defaults to ``BASE_WIDTH`` (384).
            view_height: Viewport height. Defaults to ``BASE_HEIGHT`` (216).
        """
        self.view_width = view_width
        self.view_height = view_height
        self._level_width = level_width
        self._level_height = level_height

        # Camera position (top-left of the viewport in world coords).
        self._x: float = 0.0
        self._y: float = 0.0

        # Smoothing factor for lerp follow (higher = snappier).
        self._smoothing: float = 5.0

        # Screen shake state.
        self._shake_intensity: float = 0.0
        self._shake_duration: float = 0.0
        self._shake_timer: float = 0.0
        self._shake_offset_x: float = 0.0
        self._shake_offset_y: float = 0.0

    # ── Public API ─────────────────────────────────────────────────

    def follow(self, target_rect: pygame.Rect, dt: float) -> None:
        """Move the camera towards centering the target.

        Uses linear interpolation for smooth following.

        Args:
            target_rect: The rectangle to follow (world coordinates).
            dt: Delta time in seconds.
        """
        # Desired camera position: center the target on screen.
        target_x = target_rect.centerx - self.view_width / 2
        target_y = target_rect.centery - self.view_height / 2

        # Lerp towards the target.
        factor = min(1.0, self._smoothing * dt)
        self._x += (target_x - self._x) * factor
        self._y += (target_y - self._y) * factor

        self._clamp()

    def shake(self, intensity: float, duration: float) -> None:
        """Start a screen-shake effect.

        Args:
            intensity: Maximum random offset in pixels.
            duration: How long the shake lasts in seconds.
        """
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = duration

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Convert a world-space rect to screen-space using camera offset.

        Args:
            rect: A rectangle in world coordinates.

        Returns:
            A new ``pygame.Rect`` offset by the camera position.
        """
        ox, oy = self.offset
        return pygame.Rect(rect.x - ox, rect.y - oy, rect.width, rect.height)

    def update(self, dt: float) -> None:
        """Update shake timer and compute shake offset.

        Should be called once per frame after ``follow()``.

        Args:
            dt: Delta time in seconds.
        """
        if self._shake_timer > 0:
            self._shake_timer -= dt
            # Decay intensity linearly.
            progress = max(0.0, self._shake_timer / self._shake_duration)
            current_intensity = self._shake_intensity * progress
            self._shake_offset_x = random.uniform(
                -current_intensity, current_intensity
            )
            self._shake_offset_y = random.uniform(
                -current_intensity, current_intensity
            )
        else:
            self._shake_offset_x = 0.0
            self._shake_offset_y = 0.0

    @property
    def offset(self) -> tuple[int, int]:
        """Camera offset including shake, suitable for rendering.

        Returns:
            ``(offset_x, offset_y)`` in world-pixel coordinates.
        """
        return (
            int(self._x + self._shake_offset_x),
            int(self._y + self._shake_offset_y),
        )

    # ── Private helpers ────────────────────────────────────────────

    def _clamp(self) -> None:
        """Clamp camera so the viewport stays within level bounds."""
        max_x = max(0, self._level_width - self.view_width)
        max_y = max(0, self._level_height - self.view_height)
        self._x = max(0.0, min(self._x, float(max_x)))
        self._y = max(0.0, min(self._y, float(max_y)))
