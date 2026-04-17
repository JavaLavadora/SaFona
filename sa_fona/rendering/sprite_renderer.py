"""Sprite rendering with placeholder colored rectangles and animation support."""

from __future__ import annotations

from typing import Any

import pygame


# Color mapping for placeholder sprites based on asset ID substrings.
_PLACEHOLDER_COLORS: list[tuple[str, tuple[int, int, int]]] = [
    ("ramon", (50, 100, 200)),
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


class Animation:
    """Plays a sequence of frames with per-frame durations.

    Attributes:
        loop: Whether the animation loops after the last frame.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_durations: list[float],
        loop: bool = True,
    ) -> None:
        """Initialize the animation.

        Args:
            frames: List of pygame Surfaces, one per animation frame.
            frame_durations: Duration in seconds for each frame.
            loop: Whether to loop back to frame 0 after the last frame.

        Raises:
            ValueError: If frames and frame_durations have different lengths.
        """
        if len(frames) != len(frame_durations):
            raise ValueError(
                f"frames ({len(frames)}) and frame_durations "
                f"({len(frame_durations)}) must have the same length"
            )
        self._frames = frames
        self._frame_durations = frame_durations
        self.loop = loop
        self._current_index: int = 0
        self._elapsed: float = 0.0
        self._finished: bool = False

    def update(self, dt: float) -> None:
        """Advance the animation by dt seconds.

        Args:
            dt: Delta time in seconds since the last update.
        """
        if self._finished:
            return

        self._elapsed += dt
        while self._elapsed >= self._frame_durations[self._current_index]:
            self._elapsed -= self._frame_durations[self._current_index]
            self._current_index += 1

            if self._current_index >= len(self._frames):
                if self.loop:
                    self._current_index = 0
                else:
                    self._current_index = len(self._frames) - 1
                    self._finished = True
                    break

    def reset(self) -> None:
        """Reset the animation to the first frame."""
        self._current_index = 0
        self._elapsed = 0.0
        self._finished = False

    @property
    def current_frame(self) -> pygame.Surface:
        """Return the current animation frame surface.

        Returns:
            The pygame Surface for the current frame.
        """
        return self._frames[self._current_index]

    @property
    def finished(self) -> bool:
        """Whether the animation has finished (only relevant for non-looping).

        Returns:
            True if the animation played through and is not looping.
        """
        return self._finished


class SpriteRenderer:
    """Loads asset manifest and generates colored placeholder surfaces.

    Since no real sprites exist yet, this generates colored rectangles based
    on asset IDs and caches them. When real assets are added, only the
    load_sprite_sheet method needs to change.

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
        """Load (or generate placeholder for) a sprite sheet.

        Generates colored rectangle frames based on the manifest entry.
        Frames are cached for subsequent get_frame calls.

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
        color = _color_for_asset(asset_id)

        frames: list[pygame.Surface] = []
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
