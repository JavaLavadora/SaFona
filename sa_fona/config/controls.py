"""Control-binding loader for Sa Fona.

Reads the default keyboard and gamepad bindings from
``controls_default.json`` and maps human-readable key names to
Pygame key constants so the input handler can look up bindings
at runtime without hard-coding them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pygame

from sa_fona.config.settings import DATA_DIR

# ── Key-name to Pygame constant mapping ─────────────────────────
_KEY_NAME_MAP: dict[str, int] = {
    "a": pygame.K_a,
    "b": pygame.K_b,
    "c": pygame.K_c,
    "d": pygame.K_d,
    "e": pygame.K_e,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,
    "q": pygame.K_q,
    "x": pygame.K_x,
    "z": pygame.K_z,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "space": pygame.K_SPACE,
    "escape": pygame.K_ESCAPE,
    "return": pygame.K_RETURN,
}

_DEFAULT_CONTROLS_PATH: Path = DATA_DIR / "controls_default.json"


def load_controls(path: Path | None = None) -> dict[str, Any]:
    """Load control bindings from a JSON file.

    Args:
        path: Optional path to a controls JSON file.  Falls back to
            ``controls_default.json`` inside the data directory.

    Returns:
        The parsed JSON as a dictionary with ``"keyboard"`` and
        ``"gamepad"`` sections.

    Raises:
        FileNotFoundError: If the controls file does not exist.
    """
    controls_path = path or _DEFAULT_CONTROLS_PATH
    with open(controls_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_keyboard_bindings(
    controls: dict[str, Any] | None = None,
) -> dict[str, list[int]]:
    """Convert string key names to Pygame key constants.

    Args:
        controls: A controls dictionary as returned by
            :func:`load_controls`.  If *None*, the default controls
            file is loaded automatically.

    Returns:
        A mapping from action name (e.g. ``"jump"``) to a list of
        Pygame key constants (e.g. ``[pygame.K_SPACE]``).
    """
    if controls is None:
        controls = load_controls()

    keyboard_section: dict[str, list[str]] = controls.get("keyboard", {})
    resolved: dict[str, list[int]] = {}

    for action, key_names in keyboard_section.items():
        resolved[action] = [
            _KEY_NAME_MAP[name]
            for name in key_names
            if name in _KEY_NAME_MAP
        ]

    return resolved
