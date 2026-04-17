"""Tests for the Entity base class."""

import pygame
import pytest

from sa_fona.entities.entity import Entity


class ConcreteEntity(Entity):
    """Minimal concrete entity for testing the abstract base."""

    def update(self, dt: float) -> None:
        pass


class TestEntityInit:
    """Tests for Entity construction."""

    def test_position_and_size(self) -> None:
        e = ConcreteEntity(10.0, 20.0, 24, 32)
        assert e.rect.x == 10
        assert e.rect.y == 20
        assert e.rect.width == 24
        assert e.rect.height == 32

    def test_defaults(self) -> None:
        e = ConcreteEntity(0, 0, 16, 16)
        assert e.velocity == [0.0, 0.0]
        assert e.facing_right is True
        assert e.on_ground is False
        assert e.active is True
        assert e.sprite is None


class TestEntityRender:
    """Tests for Entity.render."""

    def test_render_with_no_sprite_does_nothing(self) -> None:
        e = ConcreteEntity(0, 0, 16, 16)
        surface = pygame.Surface((100, 100))
        # Should not raise.
        e.render(surface, (0, 0))

    def test_render_blits_sprite(self) -> None:
        e = ConcreteEntity(50, 60, 16, 16)
        sprite = pygame.Surface((16, 16))
        sprite.fill((255, 0, 0))
        e.sprite = sprite

        surface = pygame.Surface((200, 200))
        surface.fill((0, 0, 0))
        e.render(surface, (10, 20))

        # The sprite should be blitted at (50-10, 60-20) = (40, 40).
        pixel = surface.get_at((40, 40))
        assert pixel[0] == 255  # Red channel.

    def test_properties(self) -> None:
        e = ConcreteEntity(5.0, 10.0, 8, 8)
        assert e.x == 5.0
        assert e.y == 10.0
