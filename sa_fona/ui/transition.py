"""Screen transition effects for cutscenes and level transitions.

Provides fade-to-black and fade-to-white effects that can be used
by the cutscene system and other scenes for smooth visual transitions.
"""

from __future__ import annotations

import pygame


class Transition:
    """Screen transition effect renderer.

    Supports fade_black and fade_white effects. The transition goes from
    transparent to fully opaque at the halfway point, then fades back
    out. Scenes can use the ``is_halfway`` property to know when to
    switch content underneath the overlay.

    Example:
        transition = Transition()
        transition.start("fade_black", 1.5)
        # In update loop:
        transition.update(dt)
        if transition.is_halfway:
            switch_scene()
        transition.render(surface)
    """

    def __init__(self) -> None:
        """Initialize the transition in an inactive state."""
        self._effect: str = ""
        self._duration: float = 0.0
        self._elapsed: float = 0.0
        self._active: bool = False
        self._halfway_reached: bool = False

    @property
    def is_active(self) -> bool:
        """Whether a transition is currently playing."""
        return self._active

    @property
    def is_halfway(self) -> bool:
        """Whether the transition has reached its halfway (peak opacity) point.

        Returns True only once, on the first frame after the midpoint
        is crossed. Subsequent checks return False until a new transition
        starts.
        """
        return self._halfway_reached

    @property
    def progress(self) -> float:
        """Transition progress from 0.0 to 1.0.

        Returns:
            0.0 at start, 1.0 when complete.
        """
        if self._duration <= 0:
            return 1.0
        return min(1.0, self._elapsed / self._duration)

    def start(self, effect: str, duration: float) -> None:
        """Begin a transition effect.

        Args:
            effect: Effect type, one of "fade_black" or "fade_white".
            duration: Total duration in seconds for the full transition
                (fade in + fade out).
        """
        self._effect = effect
        self._duration = max(0.01, duration)
        self._elapsed = 0.0
        self._active = True
        self._halfway_reached = False

    def update(self, dt: float) -> None:
        """Advance the transition timer.

        Args:
            dt: Delta time in seconds.
        """
        if not self._active:
            return

        was_before_halfway = self._elapsed < (self._duration / 2.0)
        self._elapsed += dt

        # Detect halfway crossing (fire once).
        if was_before_halfway and self._elapsed >= (self._duration / 2.0):
            self._halfway_reached = True
        else:
            self._halfway_reached = False

        # Complete.
        if self._elapsed >= self._duration:
            self._active = False
            self._halfway_reached = False

    def render(self, surface: pygame.Surface) -> None:
        """Draw the transition overlay onto the surface.

        Args:
            surface: Target surface to draw the overlay on.
        """
        if not self._active:
            return

        alpha = self._compute_alpha()
        if alpha <= 0:
            return

        color = self._get_color()
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        surface.blit(overlay, (0, 0))

    def _compute_alpha(self) -> int:
        """Compute the current overlay alpha value.

        Ramps up to 255 at the halfway point, then ramps back down.

        Returns:
            Alpha value between 0 and 255.
        """
        half = self._duration / 2.0
        if self._elapsed < half:
            # Fading in: 0 -> 255.
            t = self._elapsed / half if half > 0 else 1.0
            return int(255 * t)
        else:
            # Fading out: 255 -> 0.
            t = (self._elapsed - half) / half if half > 0 else 1.0
            return int(255 * (1.0 - t))

    def _get_color(self) -> tuple[int, int, int]:
        """Get the RGB color for the current effect.

        Returns:
            An (R, G, B) tuple.
        """
        if self._effect == "fade_white":
            return (255, 255, 255)
        # Default to black.
        return (0, 0, 0)
