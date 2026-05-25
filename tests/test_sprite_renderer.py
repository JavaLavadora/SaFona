"""Tests for the SpriteRenderer and Animation classes."""

from __future__ import annotations

import pygame
import pytest

from sa_fona.rendering.animation import Animation
from sa_fona.rendering.sprite_renderer import SpriteRenderer


@pytest.fixture(autouse=True)
def _init_pygame() -> None:
    """Ensure pygame is initialized for surface creation."""
    pygame.init()


class TestSpriteRendererPlaceholders:
    """Tests for placeholder surface generation and caching."""

    def _manifest(self) -> dict:
        """Return a small test manifest."""
        return {
            "balchar_idle": {
                "frame_width": 24,
                "frame_height": 32,
                "frame_count": 4,
            },
            "bep_idle": {
                "frame_width": 16,
                "frame_height": 16,
                "frame_count": 2,
            },
            "enemy_slime": {
                "frame_width": 16,
                "frame_height": 16,
                "frame_count": 1,
            },
            "tile_grass": {
                "frame_width": 16,
                "frame_height": 16,
                "frame_count": 1,
            },
        }

    def test_load_and_get_frame_balchar_blue(self) -> None:
        """Balchar assets should produce blue (50, 100, 200) surfaces."""
        renderer = SpriteRenderer(self._manifest())
        frame = renderer.get_frame("balchar_idle", 0)

        assert frame.get_size() == (24, 32)
        assert frame.get_at((0, 0))[:3] == (50, 100, 200)

    def test_bep_asset_green(self) -> None:
        """Bep assets should produce green (50, 180, 80) surfaces."""
        renderer = SpriteRenderer(self._manifest())
        frame = renderer.get_frame("bep_idle", 0)

        assert frame.get_at((0, 0))[:3] == (50, 180, 80)

    def test_enemy_asset_red(self) -> None:
        """Enemy assets should produce red (200, 50, 50) surfaces."""
        renderer = SpriteRenderer(self._manifest())
        frame = renderer.get_frame("enemy_slime", 0)

        assert frame.get_at((0, 0))[:3] == (200, 50, 50)

    def test_default_asset_white(self) -> None:
        """Assets with no keyword match should produce white surfaces."""
        renderer = SpriteRenderer(self._manifest())
        frame = renderer.get_frame("tile_grass", 0)

        assert frame.get_at((0, 0))[:3] == (255, 255, 255)

    def test_frame_count_matches_manifest(self) -> None:
        """Number of generated frames should match manifest frame_count."""
        renderer = SpriteRenderer(self._manifest())
        renderer.load_sprite_sheet("balchar_idle")

        # All 4 frames should be accessible.
        for i in range(4):
            renderer.get_frame("balchar_idle", i)

        with pytest.raises(IndexError):
            renderer.get_frame("balchar_idle", 4)

    def test_get_frame_auto_loads(self) -> None:
        """get_frame should auto-load the sprite sheet if not loaded."""
        renderer = SpriteRenderer(self._manifest())
        # No explicit load_sprite_sheet call.
        frame = renderer.get_frame("balchar_idle", 0)

        assert frame is not None

    def test_unknown_asset_raises_key_error(self) -> None:
        """Requesting an asset not in the manifest should raise KeyError."""
        renderer = SpriteRenderer(self._manifest())

        with pytest.raises(KeyError):
            renderer.get_frame("nonexistent", 0)

    def test_cached_frames_are_same_objects(self) -> None:
        """Subsequent calls to get_frame should return the cached surface."""
        renderer = SpriteRenderer(self._manifest())
        frame_a = renderer.get_frame("balchar_idle", 0)
        frame_b = renderer.get_frame("balchar_idle", 0)

        assert frame_a is frame_b


class TestAnimation:
    """Tests for the Animation playback system."""

    def _make_frames(self, count: int) -> list[pygame.Surface]:
        """Create a list of small test surfaces."""
        return [pygame.Surface((8, 8)) for _ in range(count)]

    def test_animation_starts_at_first_frame(self) -> None:
        """A new animation should start at frame index 0."""
        frames = self._make_frames(3)
        anim = Animation(frames, [0.1, 0.1, 0.1])

        assert anim.current_frame is frames[0]
        assert not anim.finished

    def test_animation_advances_frames(self) -> None:
        """Updating past frame duration should advance to the next frame."""
        frames = self._make_frames(3)
        anim = Animation(frames, [0.1, 0.1, 0.1])

        anim.update(0.15)  # Past first frame duration.
        assert anim.current_frame is frames[1]

    def test_looping_animation_wraps_around(self) -> None:
        """A looping animation should return to frame 0 after the last frame."""
        frames = self._make_frames(2)
        anim = Animation(frames, [0.1, 0.1], loop=True)

        anim.update(0.25)  # Past both frames.
        assert anim.current_frame is frames[0]
        assert not anim.finished

    def test_non_looping_animation_finishes(self) -> None:
        """A non-looping animation should stop at the last frame."""
        frames = self._make_frames(2)
        anim = Animation(frames, [0.1, 0.1], loop=False)

        anim.update(0.25)
        assert anim.current_frame is frames[1]
        assert anim.finished

    def test_reset_returns_to_first_frame(self) -> None:
        """reset() should return the animation to the start."""
        frames = self._make_frames(2)
        anim = Animation(frames, [0.1, 0.1], loop=False)

        anim.update(0.25)
        assert anim.finished

        anim.reset()
        assert anim.current_frame is frames[0]
        assert not anim.finished

    def test_create_animation_via_renderer(self) -> None:
        """SpriteRenderer.create_animation should produce a working Animation."""
        manifest = {
            "balchar_idle": {
                "frame_width": 24,
                "frame_height": 32,
                "frame_count": 4,
            }
        }
        renderer = SpriteRenderer(manifest)
        anim = renderer.create_animation(
            "balchar_idle", [0, 1, 2, 3], [0.1, 0.1, 0.1, 0.1]
        )

        assert isinstance(anim, Animation)
        assert not anim.finished

    def test_mismatched_frames_and_durations_raises(self) -> None:
        """Animation should raise ValueError if frames/durations mismatch."""
        frames = self._make_frames(2)
        with pytest.raises(ValueError):
            Animation(frames, [0.1])
