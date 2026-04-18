"""Dialogue overlay scene that pushes on top of gameplay.

The gameplay scene remains visible underneath, dimmed by the SceneManager's
overlay rendering. This scene manages the DialogueBox and input for advancing
or skipping dialogue.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pygame

from sa_fona.config.settings import DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.ui.dialogue_box import DialogueBox


class DialogueScene(BaseScene):
    """Overlay scene for displaying dialogue sequences.

    Pushes on top of GameplayScene. The scene below is rendered and dimmed
    by the SceneManager. The player uses the interact key to advance text
    and the pause key (or interact when skippable) to skip.

    Args:
        dialogue_id: The dialogue sequence ID to look up in dialogue data.
        event_bus: Shared event bus.
        on_complete: Optional callback invoked when the dialogue finishes.
        dialogue_data: Pre-loaded dialogue data dict. If None, loads from
            standard dialogue files.
    """

    def __init__(
        self,
        dialogue_id: str,
        event_bus: EventBus,
        on_complete: Callable[[], None] | None = None,
        dialogue_data: dict | None = None,
    ) -> None:
        """Initialize the dialogue scene.

        Args:
            dialogue_id: ID of the dialogue sequence.
            event_bus: Event bus for dialogue events.
            on_complete: Called when dialogue ends.
            dialogue_data: Pre-loaded dialogue definitions.
        """
        self._dialogue_id = dialogue_id
        self._event_bus = event_bus
        self._on_complete = on_complete
        self._done = False

        # Load dialogue data.
        if dialogue_data is None:
            dialogue_data = self._load_all_dialogue()

        # Look up the specific dialogue sequence.
        entry = dialogue_data.get(dialogue_id, {})
        lines = entry.get("lines", [])
        skippable = entry.get("skippable", True)

        self._dialogue_box = DialogueBox(event_bus=event_bus)
        self._dialogue_box.start(lines, skippable=skippable)

    @property
    def is_overlay(self) -> bool:
        """This scene renders on top of gameplay."""
        return True

    @property
    def done(self) -> bool:
        """Whether the dialogue has completed."""
        return self._done

    @property
    def dialogue_box(self) -> DialogueBox:
        """The underlying dialogue box (exposed for testing)."""
        return self._dialogue_box

    def on_enter(self) -> None:
        """Scene entered."""

    def on_exit(self) -> None:
        """Scene exited."""

    def handle_input(self, input_state: InputState) -> None:
        """Process input for dialogue advancement and skipping.

        Args:
            input_state: Current frame's input snapshot.
        """
        if self._done:
            return

        if input_state.interact_pressed:
            complete = self._dialogue_box.advance()
            if complete:
                self._finish()
                return

        # Allow skipping with pause key if dialogue is skippable.
        if input_state.pause_pressed and self._dialogue_box.skippable:
            self._dialogue_box.skip()
            self._finish()

    def update(self, dt: float) -> None:
        """Update dialogue text reveal.

        Args:
            dt: Delta time in seconds.
        """
        if not self._done:
            self._dialogue_box.update(dt)

            # Check if dialogue ended (e.g. from auto-advance completing).
            if not self._dialogue_box.is_active:
                self._finish()

    def render(self, surface: pygame.Surface) -> None:
        """Render the dialogue box overlay.

        Args:
            surface: The pygame Surface to draw on.
        """
        self._dialogue_box.render(surface)

    # ── Private helpers ────────────────────────────────────────────

    def _finish(self) -> None:
        """Mark the dialogue as complete and invoke the callback."""
        self._done = True
        if self._on_complete:
            self._on_complete()

    @staticmethod
    def _load_all_dialogue() -> dict:
        """Load all dialogue JSON files and merge them into one dict.

        Returns:
            A merged dict of dialogue_id -> dialogue definition.
        """
        dialogue_dir = DATA_DIR / "dialogue"
        merged: dict = {}

        if not dialogue_dir.exists():
            return merged

        for json_file in sorted(dialogue_dir.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    merged.update(data)
            except (json.JSONDecodeError, OSError):
                pass

        return merged
