"""Pixel-perfect scaling for Sa Fona.

Manages an internal render surface at the game's native resolution
(384x216) and scales it up to the display window using integer
scaling so pixel art stays crisp.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_WIDTH, BASE_HEIGHT


class PixelScaler:
    """Creates and manages the internal render surface.

    All game rendering targets the small internal surface returned by
    :meth:`get_surface`.  On each frame, :meth:`present` scales the
    internal surface to the larger display surface.

    Attributes:
        internal_surface: The native-resolution render target.
    """

    def __init__(self) -> None:
        """Initialise the internal surface at BASE_WIDTH x BASE_HEIGHT."""
        self.internal_surface: pygame.Surface = pygame.Surface(
            (BASE_WIDTH, BASE_HEIGHT)
        )

    def get_surface(self) -> pygame.Surface:
        """Return the internal render surface.

        Returns:
            The 384x216 surface that game systems should draw on.
        """
        return self.internal_surface

    def present(self, display_surface: pygame.Surface) -> None:
        """Scale and blit the internal surface onto the display.

        Uses ``pygame.transform.scale`` with the display's current
        dimensions so the image fills the window.  For best results
        the window size should be an integer multiple of the base
        resolution.

        Args:
            display_surface: The Pygame display surface (the window).
        """
        display_size = display_surface.get_size()
        scaled = pygame.transform.scale(self.internal_surface, display_size)
        display_surface.blit(scaled, (0, 0))

    def get_scale_factor(self, display_surface: pygame.Surface) -> float:
        """Calculate the current integer scale factor.

        Args:
            display_surface: The Pygame display surface.

        Returns:
            The ratio of the display width to the base width.
        """
        return display_surface.get_width() / BASE_WIDTH
