"""Tests for sa_fona.rendering.pixel_scaler."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH, WINDOW_SCALE
from sa_fona.rendering.pixel_scaler import PixelScaler


@pytest.fixture(autouse=True)
def _init_pygame() -> None:
    """Ensure Pygame is initialised for every test in this module."""
    pygame.init()
    yield  # type: ignore[misc]
    pygame.quit()


class TestInternalSurface:
    """Verify the internal render surface dimensions."""

    def test_surface_width(self) -> None:
        scaler = PixelScaler()
        assert scaler.get_surface().get_width() == BASE_WIDTH

    def test_surface_height(self) -> None:
        scaler = PixelScaler()
        assert scaler.get_surface().get_height() == BASE_HEIGHT

    def test_surface_is_384x216(self) -> None:
        scaler = PixelScaler()
        surface = scaler.get_surface()
        assert surface.get_size() == (384, 216)


class TestPresent:
    """Verify that present() scales to the display surface correctly."""

    def test_present_fills_display(self) -> None:
        scaler = PixelScaler()
        display_w = BASE_WIDTH * WINDOW_SCALE
        display_h = BASE_HEIGHT * WINDOW_SCALE
        display = pygame.Surface((display_w, display_h))

        # Draw a known color on the internal surface.
        scaler.get_surface().fill((255, 0, 0))
        scaler.present(display)

        # The centre pixel of the display should be the scaled color.
        centre = display.get_at((display_w // 2, display_h // 2))
        assert (centre.r, centre.g, centre.b) == (255, 0, 0)

    def test_present_with_different_scale(self) -> None:
        scaler = PixelScaler()
        display = pygame.Surface((BASE_WIDTH * 2, BASE_HEIGHT * 2))

        scaler.get_surface().fill((0, 255, 0))
        scaler.present(display)

        pixel = display.get_at((10, 10))
        assert (pixel.r, pixel.g, pixel.b) == (0, 255, 0)


class TestScaleFactor:
    """Verify scale-factor calculation."""

    def test_scale_factor_3x(self) -> None:
        scaler = PixelScaler()
        display = pygame.Surface((BASE_WIDTH * 3, BASE_HEIGHT * 3))
        assert scaler.get_scale_factor(display) == 3.0

    def test_scale_factor_1x(self) -> None:
        scaler = PixelScaler()
        display = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        assert scaler.get_scale_factor(display) == 1.0
