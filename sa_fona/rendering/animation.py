"""Animation playback for sprite frame sequences."""

from __future__ import annotations

import pygame


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
