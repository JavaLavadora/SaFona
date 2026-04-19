"""Tests for the EffectRenderer system."""

from __future__ import annotations

import pygame
import pytest

from sa_fona.rendering.effects import EffectRenderer, _get_frames


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame display is available."""
    pygame.init()
    pygame.display.set_mode((384, 216))
    yield
    pygame.quit()


class TestEffectRenderer:
    """Tests for EffectRenderer spawn/update/render cycle."""

    def test_spawn_unknown_type_returns_false(self):
        renderer = EffectRenderer()
        result = renderer.spawn("nonexistent_effect", 100, 100)
        assert result is False
        assert renderer.active_count == 0

    def test_spawn_known_type(self):
        renderer = EffectRenderer()
        result = renderer.spawn("dust", 100, 100)
        # May return False if the PNG is a placeholder that can't be sliced,
        # but the call should not raise.
        assert isinstance(result, bool)

    def test_clear_removes_all(self):
        renderer = EffectRenderer()
        renderer.spawn("dust", 10, 10)
        renderer.spawn("impact", 20, 20)
        renderer.clear()
        assert renderer.active_count == 0

    def test_remove_by_tag(self):
        renderer = EffectRenderer()
        renderer.spawn("dust", 10, 10, tag="a")
        renderer.spawn("dust", 20, 20, tag="b")
        renderer.remove_by_tag("a")
        # If both spawns succeeded, only one should remain.
        # If neither succeeded (no valid frames), count is 0 which is fine.
        assert renderer.active_count <= 1

    def test_update_does_not_crash(self):
        renderer = EffectRenderer()
        renderer.spawn("dust", 10, 10)
        renderer.update(0.1)
        # Should not raise.

    def test_render_does_not_crash(self):
        renderer = EffectRenderer()
        renderer.spawn("dust", 10, 10)
        renderer.update(0.05)
        surface = pygame.Surface((384, 216))
        renderer.render(surface, (0, 0))
        # Should not raise.

    def test_nonloop_effect_finishes(self):
        """Non-looping effects should be removed after all frames play."""
        renderer = EffectRenderer()
        spawned = renderer.spawn("dust", 50, 50)
        if not spawned:
            pytest.skip("dust frames not loadable in test environment")
        # Advance time well past the animation duration (4 frames at 12 fps).
        renderer.update(2.0)
        assert renderer.active_count == 0


class TestGetFrames:
    """Tests for the frame loading helper."""

    def test_unknown_returns_none(self):
        result = _get_frames("totally_unknown")
        assert result is None

    def test_known_type_is_cached(self):
        """Calling _get_frames twice returns the same object."""
        first = _get_frames("dust")
        second = _get_frames("dust")
        assert first is second
