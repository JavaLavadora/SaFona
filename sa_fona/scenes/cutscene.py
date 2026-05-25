"""Data-driven cutscene scene for scripted sequences.

Plays a sequence of steps including dialogue, events, waits,
transitions, and level loads. Used for post-boss sequences where
the Dimoni grants a mask and a portal opens to the next world.

Cutscene definitions are loaded from JSON files in ``data/cutscenes/``
or passed as Python dicts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH, DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.rendering.effects import EffectRenderer
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.ui.dialogue_box import DialogueBox
from sa_fona.ui.transition import Transition


class CutsceneScene(BaseScene):
    """Data-driven cutscene scene that plays scripted step sequences.

    Renders as an overlay on top of the scene below (e.g. the boss arena).
    Steps advance sequentially: dialogue waits for player input, events
    publish on the EventBus, waits pause for a duration, transitions play
    visual effects, and load_level signals a level change.

    Args:
        cutscene_data: Dict with a "steps" list defining the cutscene
            sequence. Each step has a "type" and type-specific fields.
        event_bus: Shared event bus for publishing events.
        on_load_level: Callback invoked when a load_level step is reached.
            Receives the level_path string as argument.
        fast_forward: If True, dialogue steps are auto-skipped (for retry).
    """

    def __init__(
        self,
        cutscene_data: dict[str, Any],
        event_bus: EventBus,
        on_load_level: Callable[[str], None] | None = None,
        fast_forward: bool = False,
    ) -> None:
        self._event_bus = event_bus
        self._on_load_level = on_load_level
        self._fast_forward = fast_forward

        self._input_cooldown: float = 0.5

        self._steps: list[dict[str, Any]] = cutscene_data.get("steps", [])
        self._step_index: int = 0
        self._done: bool = False

        # Dialogue sub-system for dialogue steps.
        self._dialogue_box = DialogueBox(
            event_bus=event_bus,
            chars_per_second=40.0,
        )
        self._dialogue_active: bool = False

        # Wait step timer.
        self._wait_timer: float = 0.0

        # Transition effect.
        self._transition = Transition()
        self._transition_pending_next: bool = False

        # Visual effects renderer for cutscene effects (aura, portal).
        self._effects = EffectRenderer()

        # Scene manager reference (set by the boss scene or caller).
        self._scene_manager = None

        # Begin first step.
        if self._steps:
            self._start_step()
        else:
            self._done = True

    @property
    def is_overlay(self) -> bool:
        """Cutscene renders on top of the scene below."""
        return True

    @property
    def done(self) -> bool:
        """Whether the cutscene has completed all steps."""
        return self._done

    @property
    def step_index(self) -> int:
        """Current step index (for testing)."""
        return self._step_index

    @property
    def dialogue_box(self) -> DialogueBox:
        """The dialogue box (for testing)."""
        return self._dialogue_box

    @property
    def transition(self) -> Transition:
        """The transition effect (for testing)."""
        return self._transition

    @property
    def scene_manager(self):
        """Scene manager reference."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value) -> None:
        self._scene_manager = value

    # ── Scene lifecycle ────────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered."""

    def on_exit(self) -> None:
        """Scene exited."""

    def handle_input(self, input_state: InputState) -> None:
        """Process input for advancing dialogue steps.

        Space or Enter (jump_pressed or interact_pressed) advances
        dialogue. Other step types do not respond to input.

        Args:
            input_state: Current frame input snapshot.
        """
        if self._done:
            return

        if self._input_cooldown > 0:
            return

        if self._dialogue_active:
            if input_state.jump_pressed or input_state.interact_pressed:
                complete = self._dialogue_box.advance()
                if complete:
                    self._dialogue_active = False
                    self._advance_step()

    def update(self, dt: float) -> None:
        """Update the current step.

        Args:
            dt: Delta time in seconds.
        """
        if self._done:
            return

        if self._input_cooldown > 0:
            self._input_cooldown -= dt

        # Always tick effects (even during dialogue/transition).
        self._effects.update(dt)

        # Update dialogue text reveal.
        if self._dialogue_active:
            self._dialogue_box.update(dt)
            # In fast-forward mode, auto-advance dialogue.
            if self._fast_forward and self._dialogue_box.is_fully_revealed:
                complete = self._dialogue_box.advance()
                if complete:
                    self._dialogue_active = False
                    self._advance_step()
            return

        # Update transition.
        if self._transition.is_active:
            self._transition.update(dt)
            if not self._transition.is_active:
                # Transition finished.
                if self._transition_pending_next:
                    self._transition_pending_next = False
                    self._advance_step()
            return

        # Update wait timer.
        if self._step_index < len(self._steps):
            step = self._steps[self._step_index]
            if step["type"] == "wait":
                self._wait_timer -= dt
                if self._wait_timer <= 0:
                    self._advance_step()

    def render(self, surface: pygame.Surface) -> None:
        """Render the cutscene overlay.

        Draws a dimming overlay, dialogue box, and transition effects.

        Args:
            surface: Target surface.
        """
        # Solid black background for the cutscene.
        surface.fill((0, 0, 0))

        # Visual effects (aura, portal) -- rendered in screen space (0,0 offset).
        self._effects.render(surface, (0, 0))

        # Dialogue box.
        if self._dialogue_active:
            self._dialogue_box.render(surface)

        # Transition effect (on top of everything).
        if self._transition.is_active:
            self._transition.render(surface)

    # ── Step execution ─────────────────────────────────────────────

    def _start_step(self) -> None:
        """Initialize and begin the current step."""
        if self._step_index >= len(self._steps):
            self._complete()
            return

        step = self._steps[self._step_index]
        step_type = step.get("type", "")

        if step_type == "dialogue":
            self._start_dialogue_step(step)
        elif step_type == "event":
            self._start_event_step(step)
        elif step_type == "wait":
            self._start_wait_step(step)
        elif step_type == "transition":
            self._start_transition_step(step)
        elif step_type == "load_level":
            self._start_load_level_step(step)
        elif step_type == "save_immediate":
            self._start_save_immediate_step(step)
        elif step_type == "spawn_effect":
            self._start_spawn_effect_step(step)
        elif step_type == "remove_effect":
            self._start_remove_effect_step(step)
        else:
            # Unknown step type, skip it.
            self._advance_step()

    def _start_dialogue_step(self, step: dict[str, Any]) -> None:
        """Begin a dialogue step.

        In fast-forward mode, dialogue is started normally but text is
        instantly revealed. The existing auto-advance logic in update()
        handles progressing past the line on the next frame.

        Args:
            step: The step dict with "speaker" and "text" fields.
        """
        speaker = step.get("speaker", "")
        text = step.get("text", "")
        portrait = step.get("portrait", "")
        line = {"speaker": speaker, "text": text, "portrait": portrait}
        self._dialogue_box.start([line], skippable=False)
        self._dialogue_active = True
        if self._fast_forward:
            self._dialogue_box.advance()

    def _start_event_step(self, step: dict[str, Any]) -> None:
        """Execute an event step by publishing to the EventBus.

        Advances immediately after publishing.

        Args:
            step: The step dict with "event_name" and optional "event_data".
        """
        event_name = step.get("event_name", "")
        event_data = step.get("event_data", {})
        if event_name:
            self._event_bus.publish(event_name, **event_data)
        self._advance_step()

    def _start_wait_step(self, step: dict[str, Any]) -> None:
        """Begin a wait step.

        In fast-forward mode, waits are shortened to near-zero.

        Args:
            step: The step dict with "duration" field (seconds).
        """
        duration = float(step.get("duration", 1.0))
        if self._fast_forward:
            duration = 0.01
        self._wait_timer = duration

    def _start_transition_step(self, step: dict[str, Any]) -> None:
        """Begin a transition step.

        In fast-forward mode, transitions are shortened.

        Args:
            step: The step dict with "effect" and "duration" fields.
        """
        effect = step.get("effect", "fade_black")
        duration = float(step.get("duration", 1.0))
        if self._fast_forward:
            duration = 0.05
        self._transition.start(effect, duration)
        self._transition_pending_next = True

    def _start_load_level_step(self, step: dict[str, Any]) -> None:
        """Execute a load_level step.

        Invokes the on_load_level callback and completes the cutscene.

        Args:
            step: The step dict with "level_path" field.
        """
        level_path = step.get("level_path", "")
        if self._on_load_level and level_path:
            self._on_load_level(level_path)
        self._complete()

    def _start_save_immediate_step(self, step: dict[str, Any]) -> None:
        """Execute a save_immediate step.

        Publishes a ``save_requested`` event so the SaveSystem or
        supervising scene can trigger a save.

        Args:
            step: The step dict (no extra fields needed).
        """
        self._event_bus.publish("save_requested")
        self._advance_step()

    def _start_spawn_effect_step(self, step: dict[str, Any]) -> None:
        """Spawn a visual effect at a screen position.

        Advances immediately. The effect plays in the background.

        Args:
            step: The step dict with "effect_type", "x", "y", and
                optional "tag" fields.
        """
        effect_type = step.get("effect_type", "")
        x = float(step.get("x", BASE_WIDTH // 2))
        y = float(step.get("y", BASE_HEIGHT // 2))
        tag = step.get("tag", "")
        if effect_type:
            self._effects.spawn(effect_type, x, y, tag=tag)
        self._advance_step()

    def _start_remove_effect_step(self, step: dict[str, Any]) -> None:
        """Remove effects by tag.

        Args:
            step: The step dict with "tag" field.
        """
        tag = step.get("tag", "")
        if tag:
            self._effects.remove_by_tag(tag)
        self._advance_step()

    def _advance_step(self) -> None:
        """Move to the next step in the sequence."""
        self._step_index += 1
        self._start_step()

    def _complete(self) -> None:
        """Mark the cutscene as finished and remove from scene stack."""
        self._done = True
        if self._scene_manager is not None:
            try:
                if self._scene_manager.active_scene is self:
                    self._scene_manager.pop()
            except IndexError:
                pass

    # ── Static loaders ─────────────────────────────────────────────

    @staticmethod
    def load_cutscene_data(cutscene_id: str) -> dict[str, Any]:
        """Load a cutscene definition from the data/cutscenes directory.

        Args:
            cutscene_id: The cutscene filename without extension
                (e.g. "post_boss_w1").

        Returns:
            The parsed cutscene dict, or an empty dict with no steps
            if the file is missing.
        """
        path = DATA_DIR / "cutscenes" / f"{cutscene_id}.json"
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"steps": []}
