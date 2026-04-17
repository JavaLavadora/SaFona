"""Tests for the InputHandler keyboard abstraction."""

from __future__ import annotations

import json
import os
import tempfile

import pygame

from sa_fona.core.input_handler import InputHandler, InputState


def _make_bindings_file(bindings: dict) -> str:
    """Write a temporary JSON bindings file and return its path.

    Args:
        bindings: Dictionary of action -> key list mappings.

    Returns:
        Path to the temporary JSON file.
    """
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump({"keyboard": bindings}, f)
    return path


def _keydown_event(key: int) -> pygame.event.Event:
    """Create a mock KEYDOWN event.

    Args:
        key: The pygame key constant.

    Returns:
        A pygame KEYDOWN event.
    """
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def _keyup_event(key: int) -> pygame.event.Event:
    """Create a mock KEYUP event.

    Args:
        key: The pygame key constant.

    Returns:
        A pygame KEYUP event.
    """
    return pygame.event.Event(pygame.KEYUP, key=key)


class TestInputHandlerBasics:
    """Tests for InputHandler core functionality."""

    def setup_method(self) -> None:
        """Set up a handler with standard bindings for each test."""
        pygame.init()
        self._bindings = {
            "move_left": ["a", "left"],
            "move_right": ["d", "right"],
            "jump": ["space", "w", "up"],
            "attack": ["j"],
            "pause": ["escape"],
            "interact": ["e"],
            "mask_power": ["q"],
            "mask_cycle_left": ["1"],
            "mask_cycle_right": ["2"],
            "special_ammo_toggle": ["r"],
        }
        self._path = _make_bindings_file(self._bindings)
        self._handler = InputHandler(self._path)

    def teardown_method(self) -> None:
        """Remove temporary bindings file."""
        os.unlink(self._path)

    def test_process_events_returns_input_state(self) -> None:
        """process_events should return an InputState dataclass."""
        state = self._handler.process_events([])
        assert isinstance(state, InputState)

    def test_key_press_maps_to_move_left(self) -> None:
        """Pressing 'a' should set move_left and move_x to -1."""
        state = self._handler.process_events([_keydown_event(pygame.K_a)])
        assert state.move_left is True
        assert state.move_x == -1.0

    def test_key_press_maps_to_move_right(self) -> None:
        """Pressing 'd' should set move_right and move_x to 1."""
        state = self._handler.process_events([_keydown_event(pygame.K_d)])
        assert state.move_right is True
        assert state.move_x == 1.0

    def test_arrow_key_maps_to_move_left(self) -> None:
        """Pressing LEFT arrow should set move_left."""
        state = self._handler.process_events([_keydown_event(pygame.K_LEFT)])
        assert state.move_left is True

    def test_jump_pressed_on_first_frame(self) -> None:
        """Jump should be pressed and held on the frame the key goes down."""
        state = self._handler.process_events([_keydown_event(pygame.K_SPACE)])
        assert state.jump_pressed is True
        assert state.jump_held is True
        assert state.jump_released is False

    def test_jump_held_not_pressed_on_subsequent_frame(self) -> None:
        """On the second frame with key still down, jump_pressed should be False."""
        self._handler.process_events([_keydown_event(pygame.K_SPACE)])
        # Second frame: no new events, key is still logically held.
        state = self._handler.process_events([])
        assert state.jump_pressed is False
        assert state.jump_held is True

    def test_jump_released_on_keyup_frame(self) -> None:
        """When the key goes up, jump_released should be True."""
        self._handler.process_events([_keydown_event(pygame.K_SPACE)])
        state = self._handler.process_events([_keyup_event(pygame.K_SPACE)])
        assert state.jump_released is True
        assert state.jump_held is False

    def test_pause_pressed_on_escape(self) -> None:
        """Pressing ESC should set pause_pressed."""
        state = self._handler.process_events([_keydown_event(pygame.K_ESCAPE)])
        assert state.pause_pressed is True

    def test_no_input_returns_default_state(self) -> None:
        """With no events, all actions should be in default (False/0) state."""
        state = self._handler.process_events([])
        assert state.move_left is False
        assert state.move_right is False
        assert state.jump_pressed is False
        assert state.move_x == 0.0

    def test_multiple_keys_per_action(self) -> None:
        """Both 'a' and 'left' should activate move_left."""
        state_a = self._handler.process_events([_keydown_event(pygame.K_a)])
        assert state_a.move_left is True

        # Reset by releasing.
        self._handler.process_events([_keyup_event(pygame.K_a)])

        state_left = self._handler.process_events(
            [_keydown_event(pygame.K_LEFT)]
        )
        assert state_left.move_left is True

    def test_opposing_directions_cancel_move_x(self) -> None:
        """Pressing both left and right should result in move_x == 0."""
        state = self._handler.process_events(
            [_keydown_event(pygame.K_a), _keydown_event(pygame.K_d)]
        )
        assert state.move_left is True
        assert state.move_right is True
        assert state.move_x == 0.0


class TestInputHandlerRemap:
    """Tests for the remap and save_bindings functionality."""

    def setup_method(self) -> None:
        """Set up handler for remap tests."""
        pygame.init()
        self._bindings = {"jump": ["space"]}
        self._path = _make_bindings_file(self._bindings)
        self._handler = InputHandler(self._path)

    def teardown_method(self) -> None:
        """Clean up temporary file."""
        os.unlink(self._path)

    def test_remap_changes_binding(self) -> None:
        """After remapping jump to 'w', space should no longer trigger jump."""
        self._handler.remap("jump", pygame.K_w)

        # Old key should not work.
        state = self._handler.process_events([_keydown_event(pygame.K_SPACE)])
        assert state.jump_pressed is False

        # Release and try new key.
        self._handler.process_events([_keyup_event(pygame.K_SPACE)])
        state = self._handler.process_events([_keydown_event(pygame.K_w)])
        assert state.jump_pressed is True

    def test_save_bindings_writes_json(self) -> None:
        """save_bindings should write a valid JSON file with current mappings."""
        self._handler.remap("jump", pygame.K_w)
        save_path = self._path + ".saved"
        try:
            self._handler.save_bindings(save_path)
            with open(save_path) as f:
                data = json.load(f)
            assert "keyboard" in data
            assert "jump" in data["keyboard"]
            assert "w" in data["keyboard"]["jump"]
        finally:
            if os.path.exists(save_path):
                os.unlink(save_path)
