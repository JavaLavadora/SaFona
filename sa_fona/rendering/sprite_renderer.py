"""Sprite rendering with PNG loading and placeholder fallback."""

from __future__ import annotations

from typing import Any

import pygame

from sa_fona.rendering.animation import Animation
from sa_fona.rendering.asset_loader import load_frame_strip


_PLACEHOLDER_COLORS: list[tuple[str, tuple[int, int, int]]] = [
    ("balchar", (50, 100, 200)),
    ("bep", (50, 180, 80)),
    ("enemy", (200, 50, 50)),
]
_DEFAULT_COLOR: tuple[int, int, int] = (255, 255, 255)


def _color_for_asset(asset_id: str) -> tuple[int, int, int]:
    """Determine the placeholder color for a given asset ID.

    Args:
        asset_id: The asset identifier string.

    Returns:
        An (R, G, B) color tuple.
    """
    asset_lower = asset_id.lower()
    for keyword, color in _PLACEHOLDER_COLORS:
        if keyword in asset_lower:
            return color
    return _DEFAULT_COLOR


def load_sprite_sheet_from_file(
    path: str, frame_width: int, frame_height: int,
) -> list[pygame.Surface] | None:
    """Load a PNG sprite sheet and slice it into frames.

    Delegates to :func:`sa_fona.rendering.asset_loader.load_frame_strip`
    so that all sprite loading shares a single cache and code-path.

    Args:
        path: Path to the PNG file, relative to the project root.
        frame_width: Width of a single frame in pixels.
        frame_height: Height of a single frame in pixels.

    Returns:
        List of pygame Surfaces, or None if the file doesn't exist.
    """
    return load_frame_strip(path, frame_width, frame_height)


class SpriteRenderer:
    """Loads sprite sheets from PNGs with colored-rectangle fallback.

    Tries to load real sprite sheet PNGs from the asset path first.
    Falls back to generating colored rectangles when the file doesn't
    exist.

    Args:
        asset_manifest: Dictionary with asset IDs as keys. Each value is a
            dict containing at least "frame_width" and "frame_height".
    """

    def __init__(self, asset_manifest: dict[str, Any]) -> None:
        """Initialize the sprite renderer with an asset manifest.

        Args:
            asset_manifest: Mapping of asset_id to asset metadata.
                Each entry should have "frame_width" and "frame_height" keys.
        """
        self._manifest = asset_manifest
        self._sprite_cache: dict[str, list[pygame.Surface]] = {}

    def load_sprite_sheet(self, asset_id: str) -> None:
        """Load a sprite sheet from PNG, or generate a placeholder.

        Tries to load the real sprite sheet from the path in the manifest.
        Falls back to colored rectangles if the file doesn't exist.

        Args:
            asset_id: Identifier for the asset in the manifest.

        Raises:
            KeyError: If asset_id is not in the manifest.
        """
        if asset_id in self._sprite_cache:
            return

        if asset_id not in self._manifest:
            raise KeyError(f"Asset '{asset_id}' not found in manifest")

        entry = self._manifest[asset_id]
        width = entry.get("frame_width", 16)
        height = entry.get("frame_height", 16)
        num_frames = entry.get("frame_count", 1)

        path = entry.get("path")
        if path:
            frames = load_sprite_sheet_from_file(path, width, height)
            if frames is not None:
                self._sprite_cache[asset_id] = frames
                return

        color = _color_for_asset(asset_id)
        frames = []
        for _ in range(num_frames):
            surface = pygame.Surface((width, height))
            surface.fill(color)
            frames.append(surface)

        self._sprite_cache[asset_id] = frames

    def get_frame(self, asset_id: str, frame_index: int) -> pygame.Surface:
        """Get a specific frame surface for an asset.

        Loads the sprite sheet on first access if not already loaded.

        Args:
            asset_id: Identifier for the asset.
            frame_index: Zero-based index of the frame to retrieve.

        Returns:
            A pygame Surface for the requested frame.

        Raises:
            KeyError: If asset_id is not in the manifest.
            IndexError: If frame_index is out of range.
        """
        if asset_id not in self._sprite_cache:
            self.load_sprite_sheet(asset_id)

        frames = self._sprite_cache[asset_id]
        if frame_index < 0 or frame_index >= len(frames):
            raise IndexError(
                f"Frame index {frame_index} out of range for asset "
                f"'{asset_id}' (has {len(frames)} frames)"
            )
        return frames[frame_index]

    def create_animation(
        self,
        asset_id: str,
        frame_indices: list[int],
        frame_durations: list[float],
        loop: bool = True,
    ) -> Animation:
        """Create an Animation from specific frames of an asset.

        Args:
            asset_id: Identifier for the asset.
            frame_indices: List of frame indices to include in the animation.
            frame_durations: Duration in seconds for each frame.
            loop: Whether the animation loops. Defaults to True.

        Returns:
            An Animation instance.

        Raises:
            ValueError: If frame_indices and frame_durations differ in length.
        """
        frames = [self.get_frame(asset_id, idx) for idx in frame_indices]
        return Animation(frames, frame_durations, loop)
