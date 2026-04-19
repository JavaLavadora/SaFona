"""Tests for the CutsceneScene, Transition, and post-boss cutscene flow."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.scenes.cutscene import CutsceneScene
from sa_fona.ui.transition import Transition


# ── Transition tests ──────────────────────────────────────────────


class TestTransition:
    """Tests for the Transition effect class."""

    def test_inactive_by_default(self):
        t = Transition()
        assert t.is_active is False

    def test_start_activates(self):
        t = Transition()
        t.start("fade_black", 1.0)
        assert t.is_active is True

    def test_completes_after_duration(self):
        t = Transition()
        t.start("fade_black", 1.0)
        t.update(1.1)
        assert t.is_active is False

    def test_halfway_fires_once(self):
        t = Transition()
        t.start("fade_black", 2.0)
        t.update(0.5)
        assert t.is_halfway is False
        t.update(0.6)  # crosses 1.0 midpoint
        assert t.is_halfway is True
        t.update(0.1)  # next frame, no longer halfway
        assert t.is_halfway is False

    def test_progress_increases(self):
        t = Transition()
        t.start("fade_black", 2.0)
        assert t.progress == pytest.approx(0.0, abs=0.01)
        t.update(1.0)
        assert t.progress == pytest.approx(0.5, abs=0.01)
        t.update(1.0)
        assert t.progress == pytest.approx(1.0, abs=0.01)

    def test_render_does_not_crash_when_inactive(self):
        pygame.init()
        pygame.display.set_mode((384, 216))
        t = Transition()
        surface = pygame.Surface((384, 216))
        t.render(surface)  # Should not crash.
        pygame.quit()

    def test_render_does_not_crash_when_active(self):
        pygame.init()
        pygame.display.set_mode((384, 216))
        t = Transition()
        t.start("fade_white", 1.0)
        t.update(0.3)
        surface = pygame.Surface((384, 216))
        t.render(surface)  # Should not crash.
        pygame.quit()


# ── CutsceneScene tests ──────────────────────────────────────────


class TestCutsceneStepProgression:
    """Tests for step-by-step cutscene progression."""

    def test_empty_cutscene_is_done(self):
        bus = EventBus()
        scene = CutsceneScene({"steps": []}, bus)
        assert scene.done is True

    def test_single_event_step_advances_immediately(self):
        bus = EventBus()
        received = []
        bus.subscribe("test_event", lambda **kw: received.append(kw))

        scene = CutsceneScene(
            {
                "steps": [
                    {
                        "type": "event",
                        "event_name": "test_event",
                        "event_data": {"key": "val"},
                    }
                ]
            },
            bus,
        )
        # Event steps advance immediately, so cutscene completes.
        assert scene.done is True
        assert len(received) == 1
        assert received[0]["key"] == "val"

    def test_wait_step_advances_after_duration(self):
        bus = EventBus()
        scene = CutsceneScene(
            {"steps": [{"type": "wait", "duration": 1.0}]}, bus
        )
        assert scene.done is False
        scene.update(0.5)
        assert scene.done is False
        scene.update(0.6)
        assert scene.done is True

    def test_transition_step_completes(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "transition", "effect": "fade_black", "duration": 0.5}
                ]
            },
            bus,
        )
        assert scene.done is False
        # Transition needs to complete its full duration.
        scene.update(0.3)
        assert scene.done is False
        scene.update(0.3)
        assert scene.done is True

    def test_multi_step_sequence(self):
        bus = EventBus()
        events = []
        bus.subscribe("mask_acquired", lambda **kw: events.append(kw))

        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "event", "event_name": "mask_acquired", "event_data": {"mask_id": "stone_slam"}},
                    {"type": "wait", "duration": 0.5},
                    {"type": "event", "event_name": "mask_acquired", "event_data": {"mask_id": "other"}},
                ]
            },
            bus,
        )

        # First event fires immediately, then we're on the wait step.
        assert len(events) == 1
        assert scene.done is False

        # Complete the wait.
        scene.update(0.6)

        # Second event fires, cutscene done.
        assert len(events) == 2
        assert events[1]["mask_id"] == "other"
        assert scene.done is True

    def test_load_level_completes_cutscene(self):
        bus = EventBus()
        loaded_levels = []
        scene = CutsceneScene(
            {"steps": [{"type": "load_level", "level_path": "world2/level_2_1"}]},
            bus,
            on_load_level=lambda path: loaded_levels.append(path),
        )
        assert scene.done is True
        assert loaded_levels == ["world2/level_2_1"]


class TestCutsceneDialogue:
    """Tests for dialogue step behavior."""

    def test_dialogue_step_waits_for_input(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "dialogue", "speaker": "Dimoni", "text": "Hello."}
                ]
            },
            bus,
        )
        assert scene.done is False

        # Updating without input does not advance past dialogue.
        scene.update(5.0)
        assert scene.done is False

    def test_dialogue_advances_on_input(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "dialogue", "speaker": "Dimoni", "text": "Hello."}
                ]
            },
            bus,
        )

        # Reveal the text.
        scene.update(2.0)

        # First input: finish revealing (if not yet) or advance.
        state = InputState(jump_pressed=True)
        scene.handle_input(state)

        # May need a second press if first just finished revealing.
        scene.handle_input(state)

        assert scene.done is True

    def test_dialogue_advances_with_interact(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "dialogue", "speaker": "Bep", "text": "Hi!"}
                ]
            },
            bus,
        )

        scene.update(2.0)
        state = InputState(interact_pressed=True)
        scene.handle_input(state)
        scene.handle_input(state)

        assert scene.done is True


class TestCutsceneEventPublish:
    """Tests that event steps publish to EventBus correctly."""

    def test_mask_acquired_event_published(self):
        bus = EventBus()
        acquired = []
        bus.subscribe("mask_acquired", lambda **kw: acquired.append(kw))

        CutsceneScene(
            {
                "steps": [
                    {
                        "type": "event",
                        "event_name": "mask_acquired",
                        "event_data": {"mask_id": "stone_slam"},
                    }
                ]
            },
            bus,
        )

        assert len(acquired) == 1
        assert acquired[0]["mask_id"] == "stone_slam"

    def test_save_immediate_publishes_save_requested(self):
        bus = EventBus()
        saves = []
        bus.subscribe("save_requested", lambda **kw: saves.append(True))

        CutsceneScene(
            {"steps": [{"type": "save_immediate"}]},
            bus,
        )

        assert len(saves) == 1


class TestCutsceneFastForward:
    """Tests for fast-forward mode (skip dialogue on retry)."""

    def test_fast_forward_skips_dialogue(self):
        bus = EventBus()
        events = []
        bus.subscribe("test_done", lambda **kw: events.append(True))

        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "dialogue", "speaker": "Dimoni", "text": "Long speech..."},
                    {"type": "dialogue", "speaker": "Bep", "text": "Reaction."},
                    {"type": "event", "event_name": "test_done", "event_data": {}},
                ]
            },
            bus,
            fast_forward=True,
        )

        # In fast-forward mode, dialogues are skipped so the event fires
        # immediately during construction.
        assert scene.done is True
        assert len(events) == 1

    def test_fast_forward_shortens_waits(self):
        bus = EventBus()
        scene = CutsceneScene(
            {"steps": [{"type": "wait", "duration": 10.0}]},
            bus,
            fast_forward=True,
        )
        # Wait is shortened to near-zero.
        assert scene.done is False
        scene.update(0.02)
        assert scene.done is True

    def test_fast_forward_shortens_transitions(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "transition", "effect": "fade_black", "duration": 5.0}
                ]
            },
            bus,
            fast_forward=True,
        )
        # Transition shortened to 0.05s.
        assert scene.done is False
        scene.update(0.06)
        assert scene.done is True


class TestCutsceneCompletion:
    """Tests for cutscene completion state."""

    def test_cutscene_done_after_all_steps(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "event", "event_name": "e1", "event_data": {}},
                    {"type": "event", "event_name": "e2", "event_data": {}},
                ]
            },
            bus,
        )
        assert scene.done is True

    def test_unknown_step_type_skipped(self):
        bus = EventBus()
        scene = CutsceneScene(
            {"steps": [{"type": "unknown_thing"}]},
            bus,
        )
        assert scene.done is True


class TestCutsceneOverlay:
    """Tests for overlay behavior."""

    def test_is_overlay(self):
        bus = EventBus()
        scene = CutsceneScene({"steps": []}, bus)
        assert scene.is_overlay is True


class TestCutsceneRender:
    """Tests that rendering does not crash."""

    @pytest.fixture(autouse=True)
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_mode((384, 216))
        yield
        pygame.quit()

    def test_render_with_dialogue(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "dialogue", "speaker": "Dimoni", "text": "Test."}
                ]
            },
            bus,
        )
        scene.update(0.5)
        surface = pygame.Surface((384, 216))
        scene.render(surface)  # Should not crash.

    def test_render_with_transition(self):
        bus = EventBus()
        scene = CutsceneScene(
            {
                "steps": [
                    {"type": "transition", "effect": "fade_white", "duration": 1.0}
                ]
            },
            bus,
        )
        scene.update(0.3)
        surface = pygame.Surface((384, 216))
        scene.render(surface)  # Should not crash.

    def test_render_empty_cutscene(self):
        bus = EventBus()
        scene = CutsceneScene({"steps": []}, bus)
        surface = pygame.Surface((384, 216))
        scene.render(surface)  # Should not crash.


class TestCutsceneLoadData:
    """Tests for the static cutscene data loader."""

    def test_load_missing_cutscene_returns_empty(self):
        data = CutsceneScene.load_cutscene_data("nonexistent_cutscene_xyz")
        assert "steps" in data
        assert len(data["steps"]) == 0

    def test_load_post_boss_w1(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        assert "steps" in data
        assert len(data["steps"]) > 0
        # Should contain a mask_acquired event step.
        event_steps = [s for s in data["steps"] if s.get("type") == "event"]
        assert len(event_steps) >= 1
        assert event_steps[0]["event_name"] == "mask_acquired"


# ── Boss scene cutscene integration tests ─────────────────────────


class TestBossSceneCutsceneIntegration:
    """Tests for the BossScene -> CutsceneScene handoff."""

    def test_boss_scene_has_cutscene_id(self):
        """Verify BossScene accepts a cutscene_id parameter."""
        from sa_fona.scenes.boss_scene import BossScene

        bus = EventBus()
        scene = BossScene(
            boss_id="bou_de_pedra",
            event_bus=bus,
            cutscene_id="post_boss_w1",
        )
        assert scene._cutscene_id == "post_boss_w1"

    def test_boss_scene_is_retry_false_initially(self):
        """Verify is_retry starts as False."""
        from sa_fona.scenes.boss_scene import BossScene

        bus = EventBus()
        scene = BossScene(boss_id="bou_de_pedra", event_bus=bus)
        assert scene._is_retry is False

    def test_boss_scene_reset_marks_retry(self):
        """Verify _reset_fight sets is_retry to True."""
        from sa_fona.scenes.boss_scene import BossScene

        bus = EventBus()
        scene = BossScene(boss_id="bou_de_pedra", event_bus=bus)
        scene._reset_fight()
        assert scene._is_retry is True

    def test_boss_scene_cutscene_not_pushed_without_scene_manager(self):
        """Verify cutscene push is no-op without a scene manager."""
        from sa_fona.scenes.boss_scene import BossScene

        bus = EventBus()
        scene = BossScene(boss_id="bou_de_pedra", event_bus=bus)
        scene._boss_defeated = True
        scene._defeat_timer = 2.0
        scene._push_cutscene()
        assert scene._cutscene_pushed is False
