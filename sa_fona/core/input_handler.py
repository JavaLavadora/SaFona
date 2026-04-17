"""Input abstraction layer that maps raw Pygame events to logical actions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pygame


@dataclass
class InputState:
    """Snapshot of all logical input actions for one frame.

    Attributes:
        move_left: True if the player is pressing left.
        move_right: True if the player is pressing right.
        jump_pressed: True on the frame the jump key goes down.
        jump_held: True while the jump key is held.
        jump_released: True on the frame the jump key goes up.
        attack_pressed: True on the frame the attack key goes down.
        attack_held: True while the attack key is held.
        attack_released: True on the frame the attack key goes up.
        mask_power_pressed: True on the frame the mask power key goes down.
        mask_cycle_left: True on the frame the mask-cycle-left key goes down.
        mask_cycle_right: True on the frame the mask-cycle-right key goes down.
        special_ammo_toggle: True on the frame the special ammo toggle key goes down.
        pause_pressed: True on the frame the pause key goes down.
        interact_pressed: True on the frame the interact key goes down.
        move_x: Horizontal axis value from -1.0 (left) to 1.0 (right).
    """

    move_left: bool = False
    move_right: bool = False
    jump_pressed: bool = False
    jump_held: bool = False
    jump_released: bool = False
    attack_pressed: bool = False
    attack_held: bool = False
    attack_released: bool = False
    mask_power_pressed: bool = False
    mask_cycle_left: bool = False
    mask_cycle_right: bool = False
    special_ammo_toggle: bool = False
    pause_pressed: bool = False
    interact_pressed: bool = False
    move_x: float = 0.0


# Mapping from string key names used in JSON configs to pygame key constants.
_KEY_NAME_MAP: dict[str, int] = {
    "a": pygame.K_a,
    "b": pygame.K_b,
    "c": pygame.K_c,
    "d": pygame.K_d,
    "e": pygame.K_e,
    "f": pygame.K_f,
    "g": pygame.K_g,
    "h": pygame.K_h,
    "i": pygame.K_i,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,
    "m": pygame.K_m,
    "n": pygame.K_n,
    "o": pygame.K_o,
    "p": pygame.K_p,
    "q": pygame.K_q,
    "r": pygame.K_r,
    "s": pygame.K_s,
    "t": pygame.K_t,
    "u": pygame.K_u,
    "v": pygame.K_v,
    "w": pygame.K_w,
    "x": pygame.K_x,
    "y": pygame.K_y,
    "z": pygame.K_z,
    "0": pygame.K_0,
    "1": pygame.K_1,
    "2": pygame.K_2,
    "3": pygame.K_3,
    "4": pygame.K_4,
    "5": pygame.K_5,
    "6": pygame.K_6,
    "7": pygame.K_7,
    "8": pygame.K_8,
    "9": pygame.K_9,
    "space": pygame.K_SPACE,
    "return": pygame.K_RETURN,
    "escape": pygame.K_ESCAPE,
    "tab": pygame.K_TAB,
    "backspace": pygame.K_BACKSPACE,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "lshift": pygame.K_LSHIFT,
    "rshift": pygame.K_RSHIFT,
    "lctrl": pygame.K_LCTRL,
    "rctrl": pygame.K_RCTRL,
    "lalt": pygame.K_LALT,
    "ralt": pygame.K_RALT,
    "f1": pygame.K_F1,
    "f2": pygame.K_F2,
    "f3": pygame.K_F3,
    "f4": pygame.K_F4,
    "f5": pygame.K_F5,
    "f6": pygame.K_F6,
    "f7": pygame.K_F7,
    "f8": pygame.K_F8,
    "f9": pygame.K_F9,
    "f10": pygame.K_F10,
    "f11": pygame.K_F11,
    "f12": pygame.K_F12,
}

# Actions that use pressed/held/released tri-state tracking.
_TRI_STATE_ACTIONS = {"jump", "attack"}

# Actions that only care about the frame they were pressed.
_PRESS_ONLY_ACTIONS = {
    "mask_power",
    "mask_cycle_left",
    "mask_cycle_right",
    "special_ammo_toggle",
    "pause",
    "interact",
}

# Actions that are continuous (held = True while key is down).
_HELD_ACTIONS = {"move_left", "move_right"}


def _key_name_to_constant(name: str) -> int:
    """Convert a human-readable key name to a pygame key constant.

    Args:
        name: Key name string (e.g. "a", "space", "left").

    Returns:
        The corresponding pygame key constant.

    Raises:
        ValueError: If the key name is not recognized.
    """
    name_lower = name.lower()
    if name_lower in _KEY_NAME_MAP:
        return _KEY_NAME_MAP[name_lower]
    raise ValueError(f"Unknown key name: {name!r}")


class InputHandler:
    """Abstracts keyboard and gamepad input into logical actions.

    Reads raw Pygame events and produces an InputState each frame.
    Bindings are loaded from a JSON file and can be remapped at runtime.

    Args:
        bindings_path: Path to JSON file with action-to-key mappings.
    """

    def __init__(self, bindings_path: str) -> None:
        """Initialize input handler and load key bindings.

        Args:
            bindings_path: Path to JSON file containing key bindings.
                Expected format: {"action_name": ["key1", "key2"], ...}
        """
        self._bindings_path = bindings_path
        self._action_to_keys: dict[str, list[int]] = {}
        self._key_to_actions: dict[int, list[str]] = {}
        self._keys_down: set[int] = set()
        self._prev_keys_down: set[int] = set()

        self._load_bindings(bindings_path)

    def _load_bindings(self, path: str) -> None:
        """Load key bindings from a JSON file.

        Args:
            path: Path to the JSON bindings file.
        """
        with open(path, "r") as f:
            raw: dict[str, Any] = json.load(f)

        bindings_section = raw.get("keyboard", raw)

        self._action_to_keys.clear()
        self._key_to_actions.clear()

        for action, key_names in bindings_section.items():
            if not isinstance(key_names, list):
                key_names = [key_names]
            keys = [_key_name_to_constant(name) for name in key_names]
            self._action_to_keys[action] = keys
            for key in keys:
                self._key_to_actions.setdefault(key, []).append(action)

    def process_events(self, events: list[pygame.event.Event]) -> InputState:
        """Process a frame's worth of Pygame events and return the input state.

        Args:
            events: List of pygame events from pygame.event.get().

        Returns:
            An InputState snapshot for the current frame.
        """
        self._prev_keys_down = set(self._keys_down)

        for event in events:
            if event.type == pygame.KEYDOWN:
                self._keys_down.add(event.key)
            elif event.type == pygame.KEYUP:
                self._keys_down.discard(event.key)

        state = InputState()

        for action, keys in self._action_to_keys.items():
            held = any(k in self._keys_down for k in keys)
            pressed = any(
                k in self._keys_down and k not in self._prev_keys_down
                for k in keys
            )
            released = any(
                k not in self._keys_down and k in self._prev_keys_down
                for k in keys
            )

            if action in _TRI_STATE_ACTIONS:
                setattr(state, f"{action}_pressed", pressed)
                setattr(state, f"{action}_held", held)
                setattr(state, f"{action}_released", released)
            elif action in _PRESS_ONLY_ACTIONS:
                setattr(state, f"{action}_pressed", pressed)
            elif action in _HELD_ACTIONS:
                setattr(state, action, held)

        # Compute horizontal axis from move_left / move_right.
        if state.move_left and not state.move_right:
            state.move_x = -1.0
        elif state.move_right and not state.move_left:
            state.move_x = 1.0
        else:
            state.move_x = 0.0

        return state

    def remap(self, action: str, key: int) -> None:
        """Remap an action to a new key, replacing the existing binding.

        Args:
            action: The action name to remap (e.g. "jump").
            key: The pygame key constant to bind to.
        """
        # Remove old key-to-action mappings for this action.
        old_keys = self._action_to_keys.get(action, [])
        for old_key in old_keys:
            if old_key in self._key_to_actions:
                self._key_to_actions[old_key] = [
                    a for a in self._key_to_actions[old_key] if a != action
                ]
                if not self._key_to_actions[old_key]:
                    del self._key_to_actions[old_key]

        # Set new binding.
        self._action_to_keys[action] = [key]
        self._key_to_actions.setdefault(key, []).append(action)

    def save_bindings(self, path: str) -> None:
        """Save current key bindings to a JSON file.

        Args:
            path: File path to write the bindings to.
        """
        # Reverse-map pygame constants to key names.
        constant_to_name = {v: k for k, v in _KEY_NAME_MAP.items()}
        bindings: dict[str, list[str]] = {}
        for action, keys in self._action_to_keys.items():
            names = []
            for key in keys:
                name = constant_to_name.get(key)
                if name:
                    names.append(name)
            bindings[action] = names

        with open(path, "w") as f:
            json.dump({"keyboard": bindings}, f, indent=2)
