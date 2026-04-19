"""Lightweight particle-effect renderer for short-lived animated sprites.

Manages a list of active effects (dust puffs, impact flashes, auras,
portals) that play through their frame strip once and then disappear.
Looping effects (e.g. dimoni aura, portal) continue until explicitly
removed.

All frame data is loaded lazily from the asset manifest via
:mod:`sa_fona.rendering.asset_loader`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from sa_fona.rendering.asset_loader import load_frame_strip


# ── Manifest paths and frame specs for each effect type ──────────
_EFFECT_DEFS: dict[str, dict] = {
    "dust": {
        "path": "assets/effects/dust.png",
        "frame_width": 8,
        "frame_height": 8,
        "frame_count": 4,
        "fps": 12.0,
        "loop": False,
    },
    "impact": {
        "path": "assets/effects/impact.png",
        "frame_width": 12,
        "frame_height": 12,
        "frame_count": 3,
        "fps": 14.0,
        "loop": False,
    },
    "dimoni_aura": {
        "path": "assets/effects/dimoni_aura.png",
        "frame_width": 16,
        "frame_height": 16,
        "frame_count": 3,
        "fps": 6.0,
        "loop": True,
    },
    "portal": {
        "path": "assets/effects/portal.png",
        "frame_width": 24,
        "frame_height": 32,
        "frame_count": 4,
        "fps": 8.0,
        "loop": True,
    },
}

# Module-level frame cache.
_frame_cache: dict[str, list[pygame.Surface] | None] = {}


def _get_frames(effect_type: str) -> list[pygame.Surface] | None:
    """Load and cache frames for an effect type.

    Args:
        effect_type: One of the keys in ``_EFFECT_DEFS``.

    Returns:
        List of frame surfaces, or None if not available.
    """
    if effect_type in _frame_cache:
        return _frame_cache[effect_type]

    defn = _EFFECT_DEFS.get(effect_type)
    if defn is None:
        _frame_cache[effect_type] = None
        return None

    frames = load_frame_strip(
        defn["path"], defn["frame_width"], defn["frame_height"],
    )
    _frame_cache[effect_type] = frames
    return frames


@dataclass
class _ActiveEffect:
    """State for a single playing effect instance."""

    effect_type: str
    x: float
    y: float
    frames: list[pygame.Surface]
    fps: float
    loop: bool
    timer: float = 0.0
    frame_index: int = 0
    finished: bool = False
    tag: str = ""  # Optional tag for removal of looping effects.


class EffectRenderer:
    """Spawns and renders short-lived animated effects in world space.

    Usage::

        renderer = EffectRenderer()
        renderer.spawn("dust", x=100, y=200)
        # Each frame:
        renderer.update(dt)
        renderer.render(surface, camera_offset)
    """

    def __init__(self) -> None:
        self._effects: list[_ActiveEffect] = []

    @property
    def active_count(self) -> int:
        """Number of currently playing effects."""
        return len(self._effects)

    def spawn(
        self,
        effect_type: str,
        x: float,
        y: float,
        tag: str = "",
    ) -> bool:
        """Spawn an effect at the given world position.

        Args:
            effect_type: Effect name (e.g. "dust", "impact").
            x: World X coordinate (center of the effect).
            y: World Y coordinate (center of the effect).
            tag: Optional string tag for later removal of looping effects.

        Returns:
            True if the effect was spawned, False if frames were unavailable.
        """
        frames = _get_frames(effect_type)
        if frames is None:
            return False

        defn = _EFFECT_DEFS[effect_type]
        self._effects.append(
            _ActiveEffect(
                effect_type=effect_type,
                x=x,
                y=y,
                frames=frames,
                fps=defn["fps"],
                loop=defn["loop"],
                tag=tag,
            )
        )
        return True

    def remove_by_tag(self, tag: str) -> None:
        """Remove all effects with a given tag.

        Useful for stopping looping effects like auras and portals.

        Args:
            tag: The tag string to match.
        """
        self._effects = [e for e in self._effects if e.tag != tag]

    def clear(self) -> None:
        """Remove all active effects."""
        self._effects.clear()

    def update(self, dt: float) -> None:
        """Advance all active effect animations.

        Args:
            dt: Delta time in seconds.
        """
        for eff in self._effects:
            if eff.finished:
                continue
            eff.timer += dt
            frame_duration = 1.0 / eff.fps if eff.fps > 0 else 1.0
            eff.frame_index = int(eff.timer / frame_duration)

            if eff.loop:
                eff.frame_index = eff.frame_index % len(eff.frames)
            elif eff.frame_index >= len(eff.frames):
                eff.finished = True

        # Prune finished non-looping effects.
        self._effects = [e for e in self._effects if not e.finished]

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw all active effects onto the surface.

        Args:
            surface: Target surface (base resolution).
            camera_offset: Camera ``(x, y)`` offset for world-to-screen.
        """
        for eff in self._effects:
            if eff.finished or eff.frame_index >= len(eff.frames):
                continue
            frame = eff.frames[eff.frame_index]
            screen_x = int(eff.x - camera_offset[0]) - frame.get_width() // 2
            screen_y = int(eff.y - camera_offset[1]) - frame.get_height() // 2
            surface.blit(frame, (screen_x, screen_y))
