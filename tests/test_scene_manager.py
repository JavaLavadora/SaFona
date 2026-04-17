"""Tests for the SceneManager push/pop/replace lifecycle."""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pygame
import pytest

from sa_fona.core.input_handler import InputState
from sa_fona.core.scene_manager import SceneManager
from sa_fona.scenes.base_scene import BaseScene


class StubScene(BaseScene):
    """Concrete BaseScene stub for testing, recording lifecycle calls."""

    def __init__(self, name: str = "stub", overlay: bool = False) -> None:
        """Initialize with a name for identification in assertions.

        Args:
            name: Identifier for this scene instance.
            overlay: Whether this scene is an overlay.
        """
        self.name = name
        self._overlay = overlay
        self.calls: list[str] = []

    def on_enter(self) -> None:
        self.calls.append("on_enter")

    def on_exit(self) -> None:
        self.calls.append("on_exit")

    def on_resume(self) -> None:
        self.calls.append("on_resume")

    def handle_input(self, input_state: InputState) -> None:
        self.calls.append("handle_input")

    def update(self, dt: float) -> None:
        self.calls.append("update")

    def render(self, surface: pygame.Surface) -> None:
        self.calls.append("render")

    @property
    def is_overlay(self) -> bool:
        return self._overlay


class TestSceneManagerPush:
    """Tests for pushing scenes onto the stack."""

    def test_push_calls_on_enter(self) -> None:
        """Pushing a scene should call its on_enter method."""
        mgr = SceneManager()
        scene = StubScene()

        mgr.push(scene)

        assert "on_enter" in scene.calls

    def test_push_makes_scene_active(self) -> None:
        """After pushing, the scene should be the active_scene."""
        mgr = SceneManager()
        scene = StubScene("first")

        mgr.push(scene)

        assert mgr.active_scene is scene

    def test_push_multiple_scenes(self) -> None:
        """Pushing multiple scenes should make the last one active."""
        mgr = SceneManager()
        scene_a = StubScene("a")
        scene_b = StubScene("b")

        mgr.push(scene_a)
        mgr.push(scene_b)

        assert mgr.active_scene is scene_b


class TestSceneManagerPop:
    """Tests for popping scenes from the stack."""

    def test_pop_calls_on_exit(self) -> None:
        """Popping should call on_exit on the removed scene."""
        mgr = SceneManager()
        scene = StubScene()
        mgr.push(scene)

        mgr.pop()

        assert "on_exit" in scene.calls

    def test_pop_calls_on_resume_on_scene_below(self) -> None:
        """Popping should call on_resume on the scene that becomes active."""
        mgr = SceneManager()
        scene_a = StubScene("a")
        scene_b = StubScene("b")
        mgr.push(scene_a)
        mgr.push(scene_b)

        mgr.pop()

        assert "on_resume" in scene_a.calls
        assert mgr.active_scene is scene_a

    def test_pop_empty_stack_raises(self) -> None:
        """Popping an empty stack should raise IndexError."""
        mgr = SceneManager()
        with pytest.raises(IndexError):
            mgr.pop()


class TestSceneManagerReplace:
    """Tests for replacing the top scene."""

    def test_replace_calls_on_exit_on_old(self) -> None:
        """Replace should call on_exit on the old scene."""
        mgr = SceneManager()
        old_scene = StubScene("old")
        new_scene = StubScene("new")
        mgr.push(old_scene)

        mgr.replace(new_scene)

        assert "on_exit" in old_scene.calls

    def test_replace_calls_on_enter_on_new(self) -> None:
        """Replace should call on_enter on the new scene."""
        mgr = SceneManager()
        old_scene = StubScene("old")
        new_scene = StubScene("new")
        mgr.push(old_scene)

        mgr.replace(new_scene)

        assert "on_enter" in new_scene.calls

    def test_replace_makes_new_scene_active(self) -> None:
        """After replace, the new scene should be active."""
        mgr = SceneManager()
        old_scene = StubScene("old")
        new_scene = StubScene("new")
        mgr.push(old_scene)

        mgr.replace(new_scene)

        assert mgr.active_scene is new_scene

    def test_replace_empty_stack_raises(self) -> None:
        """Replacing on an empty stack should raise IndexError."""
        mgr = SceneManager()
        with pytest.raises(IndexError):
            mgr.replace(StubScene())


class TestSceneManagerActiveScene:
    """Tests for the active_scene property."""

    def test_active_scene_returns_top_of_stack(self) -> None:
        """active_scene should return the most recently pushed scene."""
        mgr = SceneManager()
        scene = StubScene()
        mgr.push(scene)

        assert mgr.active_scene is scene

    def test_active_scene_empty_raises(self) -> None:
        """Accessing active_scene on empty stack should raise IndexError."""
        mgr = SceneManager()
        with pytest.raises(IndexError):
            _ = mgr.active_scene


class TestSceneManagerUpdateAndRender:
    """Tests for update and render delegation."""

    def test_update_delegates_to_active_scene(self) -> None:
        """update should call update on the top scene."""
        mgr = SceneManager()
        scene = StubScene()
        mgr.push(scene)

        mgr.update(0.016)

        assert "update" in scene.calls

    def test_render_delegates_to_active_scene(self) -> None:
        """render should call render on the top scene."""
        pygame.init()
        mgr = SceneManager()
        scene = StubScene()
        mgr.push(scene)
        surface = pygame.Surface((384, 216))

        mgr.render(surface)

        assert "render" in scene.calls

    def test_update_on_empty_stack_does_not_crash(self) -> None:
        """Updating with no scenes should not raise."""
        mgr = SceneManager()
        mgr.update(0.016)

    def test_render_on_empty_stack_does_not_crash(self) -> None:
        """Rendering with no scenes should not raise."""
        pygame.init()
        mgr = SceneManager()
        surface = pygame.Surface((384, 216))
        mgr.render(surface)

    def test_overlay_scene_also_renders_scene_below(self) -> None:
        """When top scene is_overlay, the scene below should also be rendered."""
        pygame.init()
        mgr = SceneManager()
        below = StubScene("below")
        overlay = StubScene("overlay", overlay=True)
        mgr.push(below)
        mgr.push(overlay)
        surface = pygame.Surface((384, 216))

        mgr.render(surface)

        assert "render" in below.calls
        assert "render" in overlay.calls
