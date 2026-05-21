"""Centralized asset loading utilities for sprites, UI elements, and portraits.

Provides safe loading functions that return None when an asset file
is missing, allowing callers to fall back to placeholder rendering.
All paths are resolved relative to the project root.

Entity sprite loading should go through :func:`load_frame_strip` so
that a single cache and code-path is used project-wide.
"""

from __future__ import annotations

import json
import os
from typing import Any

import pygame

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
)

_MANIFEST_PATH = os.path.join(
    _PROJECT_ROOT, "sa_fona", "data", "asset_manifest.json"
)

_manifest_cache: dict[str, Any] | None = None
_image_cache: dict[str, pygame.Surface] = {}
_frame_strip_cache: dict[str, list[pygame.Surface]] = {}


def _get_manifest() -> dict[str, Any]:
    """Load and cache the asset manifest.

    Returns:
        The parsed manifest dict.
    """
    global _manifest_cache
    if _manifest_cache is None:
        try:
            with open(_MANIFEST_PATH, "r", encoding="utf-8") as fh:
                _manifest_cache = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            _manifest_cache = {}
    return _manifest_cache


def load_image(relative_path: str) -> pygame.Surface | None:
    """Load a single image from a path relative to project root.

    Caches the result so repeated calls are cheap.

    Args:
        relative_path: Path relative to project root (e.g. "assets/ui/title.png").

    Returns:
        A pygame Surface, or None if the file is missing or cannot be loaded.
    """
    if relative_path in _image_cache:
        return _image_cache[relative_path]

    full_path = os.path.join(_PROJECT_ROOT, relative_path)
    if not os.path.isfile(full_path):
        return None

    try:
        surface = pygame.image.load(full_path).convert_alpha()
        _image_cache[relative_path] = surface
        return surface
    except pygame.error:
        return None


def load_frame_strip(
    relative_path: str, frame_width: int, frame_height: int,
) -> list[pygame.Surface] | None:
    """Load a horizontal sprite strip and slice it into frames.

    Args:
        relative_path: Path relative to project root.
        frame_width: Width of a single frame.
        frame_height: Height of a single frame.

    Returns:
        List of frame surfaces, or None if the file is missing.
    """
    cache_key = f"{relative_path}:{frame_width}x{frame_height}"
    if cache_key in _frame_strip_cache:
        return _frame_strip_cache[cache_key]

    full_path = os.path.join(_PROJECT_ROOT, relative_path)
    if not os.path.isfile(full_path):
        return None

    try:
        sheet = pygame.image.load(full_path).convert_alpha()
    except pygame.error:
        return None

    num_frames = max(1, sheet.get_width() // frame_width)
    frames: list[pygame.Surface] = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
            frames.append(sheet.subsurface(rect).copy())

    if frames:
        _frame_strip_cache[cache_key] = frames
    return frames if frames else None


def load_ui_asset(asset_key: str) -> pygame.Surface | None:
    """Load a UI asset by its manifest key.

    Looks up the path in the manifest's "ui" section.

    Args:
        asset_key: Key in the manifest (e.g. "title", "game_over").

    Returns:
        A pygame Surface, or None if not found.
    """
    manifest = _get_manifest()
    ui_section = manifest.get("ui", {})
    entry = ui_section.get(asset_key)
    if entry is None:
        return None
    path = entry.get("path")
    if not path:
        return None
    return load_image(path)


def load_ui_frame_strip(asset_key: str) -> list[pygame.Surface] | None:
    """Load a UI frame strip asset by its manifest key.

    For assets like hud_heart (3-frame strip) or charge_indicator.

    Args:
        asset_key: Key in the manifest's "ui" section.

    Returns:
        List of frame surfaces, or None if not found.
    """
    manifest = _get_manifest()
    ui_section = manifest.get("ui", {})
    entry = ui_section.get(asset_key)
    if entry is None:
        return None
    path = entry.get("path")
    fw = entry.get("frame_width")
    fh = entry.get("frame_height")
    if not path or not fw or not fh:
        return None
    return load_frame_strip(path, fw, fh)


def load_portrait(portrait_key: str) -> pygame.Surface | None:
    """Load a portrait image by its manifest key.

    If the loaded image is larger than the manifest dimensions (e.g.
    an 88x88 PNG when the manifest specifies 44x44), it is scaled
    down to fit.

    Args:
        portrait_key: Key in the manifest's "portraits" section
            (e.g. "ramon_neutral", "bep_happy").

    Returns:
        A pygame Surface, or None if not found.
    """
    manifest = _get_manifest()
    portraits_section = manifest.get("portraits", {})
    entry = portraits_section.get(portrait_key)
    if entry is None:
        return None
    path = entry.get("path")
    if not path:
        return None
    surface = load_image(path)
    if surface is None:
        return None
    target_w = entry.get("width")
    target_h = entry.get("height")
    if (
        target_w
        and target_h
        and (surface.get_width() != target_w or surface.get_height() != target_h)
    ):
        surface = pygame.transform.smoothscale(surface, (target_w, target_h))
    return surface


def clear_caches() -> None:
    """Reset all module-level caches in this module.

    Useful for level transitions and testing where loaded assets
    should be freed or reloaded from disk.
    """
    global _manifest_cache
    _manifest_cache = None
    _image_cache.clear()
    _frame_strip_cache.clear()


def clear_all_caches() -> None:
    """Reset every asset cache across the project.

    Calls :func:`clear_caches` for this module, plus the per-module
    clear functions in ``effects`` and ``bou_de_pedra``.
    """
    clear_caches()

    # Import peer modules lazily to avoid circular imports at the
    # module level -- they already depend on us.
    from sa_fona.rendering.effects import clear_caches as _clear_effects
    from sa_fona.entities.bosses.bou_de_pedra import (
        clear_caches as _clear_boss,
    )

    _clear_effects()
    _clear_boss()
