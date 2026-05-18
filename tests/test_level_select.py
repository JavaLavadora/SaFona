"""Tests for the LevelSelectScene and level discovery."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.core.scene_manager import SceneManager
from sa_fona.scenes.level_select import LevelSelectScene, discover_levels


class TestDiscoverLevels:
    """Tests for the discover_levels utility function."""

    def test_returns_list(self):
        result = discover_levels()
        assert isinstance(result, list)

    def test_finds_world1_levels(self):
        result = discover_levels()
        world1 = [l for l in result if l["world"] == "world1"]
        assert len(world1) >= 4

    def test_finds_world2_levels(self):
        result = discover_levels()
        world2 = [l for l in result if l["world"] == "world2"]
        assert len(world2) >= 1

    def test_finds_test_levels(self):
        result = discover_levels()
        test = [l for l in result if l["world"] == "test"]
        assert len(test) >= 1

    def test_display_names_are_readable(self):
        result = discover_levels()
        names = [l["display_name"] for l in result]
        assert any("World 1" in n for n in names)

    def test_test_levels_sorted_last(self):
        result = discover_levels()
        if len(result) >= 2:
            test_levels = [l for l in result if l["world"] == "test"]
            if test_levels:
                last_entry = result[-1]
                assert last_entry["world"] == "test"


class TestLevelSelectScene:
    """Tests for the LevelSelectScene navigation and selection."""

    def _make_scene(self) -> LevelSelectScene:
        """Create a LevelSelectScene with a scene manager."""
        bus = EventBus()
        scene = LevelSelectScene(event_bus=bus)
        mgr = SceneManager()
        scene.scene_manager = mgr
        mgr.push(scene)
        return scene

    def test_initial_state(self):
        scene = self._make_scene()
        # "Back" at index 0, first level at index 1 -- starts at 1.
        assert scene.selected == 1
        assert scene.entries[0] == "< Back"
        assert len(scene.entries) > 1

    def test_navigate_down(self):
        scene = self._make_scene()
        initial = scene.selected
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 1

    def test_navigate_up(self):
        scene = self._make_scene()
        # Move down first, then back up.
        scene.handle_input(InputState(move_right=True))
        pos = scene.selected
        scene.handle_input(InputState(move_left=True))
        assert scene.selected == pos - 1

    def test_navigate_up_clamps_at_zero(self):
        scene = self._make_scene()
        # Move to top.
        for _ in range(20):
            scene.handle_input(InputState(move_left=True))
        assert scene.selected == 0

    def test_navigate_down_clamps_at_end(self):
        scene = self._make_scene()
        for _ in range(100):
            scene.handle_input(InputState(move_right=True))
        assert scene.selected == len(scene.entries) - 1

    def test_back_action(self):
        scene = self._make_scene()
        mgr = scene.scene_manager
        # Navigate to "Back" (index 0).
        for _ in range(20):
            scene.handle_input(InputState(move_left=True))
        assert scene.selected == 0
        # Confirm.
        scene.handle_input(InputState(jump_pressed=True))
        scene.update(0.016)
        # Scene manager should have replaced to MainMenuScene.
        from sa_fona.scenes.main_menu import MainMenuScene
        assert isinstance(mgr.active_scene, MainMenuScene)

    def test_esc_returns_to_menu(self):
        scene = self._make_scene()
        mgr = scene.scene_manager
        scene.handle_input(InputState(pause_pressed=True))
        scene.update(0.016)
        from sa_fona.scenes.main_menu import MainMenuScene
        assert isinstance(mgr.active_scene, MainMenuScene)

    def test_select_level_loads_gameplay(self):
        scene = self._make_scene()
        mgr = scene.scene_manager
        # Ensure we are on a valid level entry (index 1).
        assert scene.selected == 1
        # Confirm selection.
        scene.handle_input(InputState(jump_pressed=True))
        scene.update(0.016)
        from sa_fona.scenes.gameplay import GameplayScene
        assert isinstance(mgr.active_scene, GameplayScene)

    def test_interact_also_confirms(self):
        scene = self._make_scene()
        mgr = scene.scene_manager
        scene.handle_input(InputState(interact_pressed=True))
        scene.update(0.016)
        from sa_fona.scenes.gameplay import GameplayScene
        assert isinstance(mgr.active_scene, GameplayScene)

    def test_move_down_input_navigates(self):
        scene = self._make_scene()
        initial = scene.selected
        scene.handle_input(InputState(move_down=True))
        assert scene.selected == initial + 1


class TestLevelSelectRender:
    """Tests that rendering does not crash."""

    @pytest.fixture(autouse=True)
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_mode((384, 216))
        yield
        pygame.quit()

    def test_render_does_not_crash(self):
        bus = EventBus()
        scene = LevelSelectScene(event_bus=bus)
        surface = pygame.Surface((384, 216))
        scene.render(surface)

    def test_render_with_selection(self):
        bus = EventBus()
        scene = LevelSelectScene(event_bus=bus)
        scene.handle_input(InputState(move_right=True))
        surface = pygame.Surface((384, 216))
        scene.render(surface)
