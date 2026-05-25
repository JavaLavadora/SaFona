"""Tests for the dialogue system: DialogueBox and DialogueScene."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.ui.dialogue_box import DialogueBox


# Sample dialogue data for tests.
_SAMPLE_LINES = [
    {"speaker": "bep", "portrait": "bep_excited", "text": "Hello, Balchar!"},
    {"speaker": "balchar", "portrait": "balchar_annoyed", "text": "Leave me alone."},
]

_SINGLE_LINE = [
    {"speaker": "bep", "portrait": "bep_excited", "text": "Just one line."},
]


class TestDialogueBoxInit:
    """Tests for DialogueBox initialization."""

    def test_not_active_initially(self):
        box = DialogueBox()
        assert box.is_active is False

    def test_start_activates(self):
        box = DialogueBox()
        box.start(_SAMPLE_LINES)
        assert box.is_active is True

    def test_start_empty_sequence_stays_inactive(self):
        box = DialogueBox()
        box.start([])
        assert box.is_active is False

    def test_current_index_starts_at_zero(self):
        box = DialogueBox()
        box.start(_SAMPLE_LINES)
        assert box.current_index == 0


class TestDialogueBoxLetterReveal:
    """Tests for letter-by-letter text reveal."""

    def test_revealed_chars_starts_at_zero(self):
        box = DialogueBox(chars_per_second=10.0)
        box.start(_SAMPLE_LINES)
        assert box.revealed_chars == 0

    def test_update_reveals_chars(self):
        box = DialogueBox(chars_per_second=10.0)
        box.start(_SAMPLE_LINES)
        box.update(0.5)  # 0.5s * 10 chars/s = 5 chars
        assert box.revealed_chars == 5

    def test_update_does_not_exceed_text_length(self):
        box = DialogueBox(chars_per_second=100.0)
        box.start(_SINGLE_LINE)
        box.update(10.0)  # Way more than needed.
        text = _SINGLE_LINE[0]["text"]
        assert box.revealed_chars == len(text)

    def test_is_fully_revealed_after_enough_time(self):
        box = DialogueBox(chars_per_second=100.0)
        box.start(_SINGLE_LINE)
        box.update(10.0)
        assert box.is_fully_revealed is True

    def test_not_fully_revealed_initially(self):
        box = DialogueBox(chars_per_second=10.0)
        box.start(_SAMPLE_LINES)
        assert box.is_fully_revealed is False


class TestDialogueBoxAdvance:
    """Tests for advance behavior."""

    def test_advance_finishes_reveal_first(self):
        box = DialogueBox(chars_per_second=10.0)
        box.start(_SAMPLE_LINES)
        # Text not yet fully revealed.
        result = box.advance()
        assert result is False
        # Now text should be fully revealed.
        assert box.is_fully_revealed is True
        assert box.current_index == 0

    def test_advance_moves_to_next_line(self):
        box = DialogueBox(chars_per_second=1000.0)
        box.start(_SAMPLE_LINES)
        box.update(10.0)  # Fully reveal first line.
        result = box.advance()
        assert result is False
        assert box.current_index == 1
        assert box.revealed_chars == 0

    def test_advance_past_last_line_completes(self):
        box = DialogueBox(chars_per_second=1000.0)
        box.start(_SINGLE_LINE)
        box.update(10.0)
        result = box.advance()
        assert result is True
        assert box.is_active is False

    def test_full_two_line_sequence(self):
        box = DialogueBox(chars_per_second=1000.0)
        box.start(_SAMPLE_LINES)

        # Reveal + advance line 1.
        box.update(10.0)
        result = box.advance()
        assert result is False
        assert box.current_index == 1

        # Reveal + advance line 2.
        box.update(10.0)
        result = box.advance()
        assert result is True
        assert box.is_active is False

    def test_advance_on_inactive_returns_true(self):
        box = DialogueBox()
        assert box.advance() is True


class TestDialogueBoxSkip:
    """Tests for dialogue skipping."""

    def test_skip_when_skippable(self):
        box = DialogueBox()
        box.start(_SAMPLE_LINES, skippable=True)
        box.skip()
        assert box.is_active is False

    def test_skip_when_not_skippable(self):
        box = DialogueBox()
        box.start(_SAMPLE_LINES, skippable=False)
        box.skip()
        assert box.is_active is True  # Should not skip.

    def test_skippable_property(self):
        box = DialogueBox()
        box.start(_SAMPLE_LINES, skippable=False)
        assert box.skippable is False


class TestDialogueBoxEvents:
    """Tests for EventBus integration."""

    def test_start_publishes_dialogue_started(self):
        bus = EventBus()
        events = []
        bus.subscribe("dialogue_started", lambda: events.append("started"))
        box = DialogueBox(event_bus=bus)
        box.start(_SAMPLE_LINES)
        assert "started" in events

    def test_complete_publishes_dialogue_ended(self):
        bus = EventBus()
        events = []
        bus.subscribe("dialogue_ended", lambda: events.append("ended"))
        box = DialogueBox(event_bus=bus, chars_per_second=1000.0)
        box.start(_SINGLE_LINE)
        box.update(10.0)
        box.advance()
        assert "ended" in events

    def test_skip_publishes_dialogue_ended(self):
        bus = EventBus()
        events = []
        bus.subscribe("dialogue_ended", lambda: events.append("ended"))
        box = DialogueBox(event_bus=bus)
        box.start(_SAMPLE_LINES, skippable=True)
        box.skip()
        assert "ended" in events


class TestDialogueBoxAutoAdvance:
    """Tests for auto-advance functionality."""

    def test_auto_advance_moves_to_next_line(self):
        lines = [
            {"speaker": "narrator", "text": "Short.", "auto_advance_ms": 500},
            {"speaker": "narrator", "text": "Second."},
        ]
        box = DialogueBox(chars_per_second=1000.0)
        box.start(lines)
        # Use a small dt to reveal text without triggering auto-advance.
        box.update(0.01)
        assert box.is_fully_revealed is True
        assert box.current_index == 0
        # Now wait for auto-advance (accumulate past 500ms threshold).
        box.update(0.6)
        assert box.current_index == 1

    def test_auto_advance_completes_sequence(self):
        lines = [
            {"speaker": "narrator", "text": "Only.", "auto_advance_ms": 200},
        ]
        box = DialogueBox(chars_per_second=1000.0)
        box.start(lines)
        # Small dt to reveal text without triggering auto-advance.
        box.update(0.01)
        assert box.is_fully_revealed is True
        # Now accumulate past the 200ms auto-advance threshold.
        box.update(0.3)
        assert box.is_active is False


class TestDialogueBoxRender:
    """Tests that render does not crash."""

    @pytest.fixture(autouse=True)
    def _init_pygame(self):
        """Initialize pygame with display and font for render tests."""
        pygame.init()
        pygame.display.set_mode((384, 216))
        yield
        pygame.quit()

    def test_render_active(self):
        box = DialogueBox(chars_per_second=10.0)
        box.start(_SAMPLE_LINES)
        box.update(0.1)
        surface = pygame.Surface((384, 216))
        box.render(surface)  # Should not crash.

    def test_render_inactive(self):
        box = DialogueBox()
        surface = pygame.Surface((384, 216))
        box.render(surface)  # Should not crash.


class TestDialogueScene:
    """Tests for the DialogueScene overlay."""

    def test_is_overlay(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        dialogue_data = {
            "test_d": {
                "skippable": True,
                "lines": [{"speaker": "bep", "text": "Hi!"}],
            }
        }
        scene = DialogueScene("test_d", bus, dialogue_data=dialogue_data)
        assert scene.is_overlay is True

    def test_advance_with_interact(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        dialogue_data = {
            "test_d": {
                "skippable": True,
                "lines": [{"speaker": "bep", "text": "Hi!"}],
            }
        }
        scene = DialogueScene("test_d", bus, dialogue_data=dialogue_data)

        # First interact: finish revealing text.
        state = InputState(interact_pressed=True)
        scene.handle_input(state)

        # Second interact: advance past last line, dialogue completes.
        scene.handle_input(state)
        assert scene.done is True

    def test_skip_with_pause(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        dialogue_data = {
            "test_d": {
                "skippable": True,
                "lines": [
                    {"speaker": "bep", "text": "First."},
                    {"speaker": "bep", "text": "Second."},
                ],
            }
        }
        scene = DialogueScene("test_d", bus, dialogue_data=dialogue_data)
        state = InputState(pause_pressed=True)
        scene.handle_input(state)
        assert scene.done is True

    def test_non_skippable_ignores_pause(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        dialogue_data = {
            "test_d": {
                "skippable": False,
                "lines": [{"speaker": "bep", "text": "Can't skip this!"}],
            }
        }
        scene = DialogueScene("test_d", bus, dialogue_data=dialogue_data)
        state = InputState(pause_pressed=True)
        scene.handle_input(state)
        assert scene.done is False

    def test_on_complete_callback(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        completed = []
        dialogue_data = {
            "test_d": {
                "skippable": True,
                "lines": [{"speaker": "bep", "text": "Hi!"}],
            }
        }
        scene = DialogueScene(
            "test_d", bus, on_complete=lambda: completed.append(True),
            dialogue_data=dialogue_data,
        )
        state = InputState(interact_pressed=True)
        scene.handle_input(state)  # Finish reveal.
        scene.handle_input(state)  # Advance past last -> complete.
        assert completed == [True]

    def test_unknown_dialogue_id_starts_empty(self):
        from sa_fona.scenes.dialogue import DialogueScene

        bus = EventBus()
        dialogue_data = {}
        scene = DialogueScene("nonexistent", bus, dialogue_data=dialogue_data)
        # Dialogue box never activated because lines are empty.
        assert scene.dialogue_box.is_active is False
