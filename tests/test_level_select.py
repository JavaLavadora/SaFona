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
        # Press right (edge triggers on first press).
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 1

    def test_navigate_up(self):
        scene = self._make_scene()
        # Move down first (press then release to reset edge state).
        scene.handle_input(InputState(move_right=True))
        scene.handle_input(InputState())  # Release.
        pos = scene.selected
        scene.handle_input(InputState(move_left=True))
        assert scene.selected == pos - 1

    def test_navigate_up_clamps_at_zero(self):
        scene = self._make_scene()
        # Move to top — simulate press/release cycles for edge detection.
        for _ in range(20):
            scene.handle_input(InputState(move_left=True))
            scene.handle_input(InputState())  # Release.
        assert scene.selected == 0

    def test_navigate_down_clamps_at_end(self):
        scene = self._make_scene()
        # Simulate press/release cycles for edge detection.
        for _ in range(100):
            scene.handle_input(InputState(move_right=True))
            scene.handle_input(InputState())  # Release.
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


class TestDiscoverBosses:
    """Tests for boss discovery in the level select."""

    def test_boss_entry_exists(self):
        result = discover_levels()
        boss_entries = [l for l in result if l.get("boss_id")]
        assert len(boss_entries) >= 1

    def test_boss_entry_has_display_name(self):
        result = discover_levels()
        boss_entries = [l for l in result if l.get("boss_id")]
        assert any("Boss" in b["display_name"] for b in boss_entries)

    def test_boss_entry_placed_after_world_levels(self):
        result = discover_levels()
        # Find the world1 boss entry and verify it comes after world1 levels.
        boss_idx = None
        last_w1_level_idx = None
        for i, entry in enumerate(result):
            if entry.get("boss_id") and entry["world"] == "world1":
                boss_idx = i
            elif entry["world"] == "world1" and not entry.get("boss_id"):
                last_w1_level_idx = i
        if boss_idx is not None and last_w1_level_idx is not None:
            assert boss_idx > last_w1_level_idx

    def test_boss_has_boss_id_key(self):
        result = discover_levels()
        boss_entries = [l for l in result if l.get("boss_id")]
        assert boss_entries[0]["boss_id"] == "bou_de_pedra"


class TestLevelSelectDebounce:
    """Tests for edge-detection input debounce in the level select."""

    def _make_scene(self) -> LevelSelectScene:
        bus = EventBus()
        scene = LevelSelectScene(event_bus=bus)
        mgr = SceneManager()
        scene.scene_manager = mgr
        mgr.push(scene)
        return scene

    def test_held_key_does_not_repeat(self):
        """Holding a key should only move once."""
        scene = self._make_scene()
        initial = scene.selected
        # First press moves.
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 1
        # Held key (same state) does not move further.
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 1

    def test_release_and_repress_moves_again(self):
        """Releasing and re-pressing should move again."""
        scene = self._make_scene()
        initial = scene.selected
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 1
        # Release.
        scene.handle_input(InputState())
        # Re-press.
        scene.handle_input(InputState(move_right=True))
        assert scene.selected == initial + 2
