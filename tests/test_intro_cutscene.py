"""Tests for the intro cutscene data and main menu integration."""

import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.core.scene_manager import SceneManager
from sa_fona.scenes.cutscene import CutsceneScene
from sa_fona.scenes.main_menu import MainMenuScene


class TestIntroCutsceneData:
    """Tests for the intro.json cutscene data file."""

    def test_intro_cutscene_loads(self):
        data = CutsceneScene.load_cutscene_data("intro")
        assert "steps" in data
        assert len(data["steps"]) > 0

    def test_intro_starts_with_transition(self):
        data = CutsceneScene.load_cutscene_data("intro")
        first_step = data["steps"][0]
        assert first_step["type"] == "transition"
        assert first_step["effect"] == "fade_black"

    def test_intro_contains_dialogue(self):
        data = CutsceneScene.load_cutscene_data("intro")
        dialogue_steps = [s for s in data["steps"] if s["type"] == "dialogue"]
        assert len(dialogue_steps) >= 5  # Multiple characters speaking

    def test_intro_has_key_characters(self):
        data = CutsceneScene.load_cutscene_data("intro")
        speakers = {s.get("speaker", "") for s in data["steps"] if s["type"] == "dialogue"}
        assert "Ramon" in speakers
        assert "Bep" in speakers
        assert "Es Dimoni de Sant Joan" in speakers

    def test_intro_has_dimoni_effect(self):
        data = CutsceneScene.load_cutscene_data("intro")
        spawn_steps = [s for s in data["steps"] if s["type"] == "spawn_effect"]
        assert len(spawn_steps) >= 1
        effect_types = {s["effect_type"] for s in spawn_steps}
        assert "dimoni_aura" in effect_types

    def test_intro_cutscene_plays_in_fast_forward(self):
        """Verify the intro cutscene can be played through without errors."""
        data = CutsceneScene.load_cutscene_data("intro")
        bus = EventBus()
        scene = CutsceneScene(data, bus, fast_forward=True)

        # Run through the cutscene in fast-forward.
        for _ in range(200):
            if scene.done:
                break
            scene.update(0.016)

        assert scene.done is True


class TestPostBossW1CutsceneData:
    """Tests for the rewritten post_boss_w1.json cutscene data."""

    def test_loads_successfully(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        assert "steps" in data
        assert len(data["steps"]) > 0

    def test_has_mask_acquired_event(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        event_steps = [s for s in data["steps"] if s.get("type") == "event"]
        assert len(event_steps) >= 1
        assert event_steps[0]["event_name"] == "mask_acquired"
        assert event_steps[0]["event_data"]["mask_id"] == "stone_slam"

    def test_has_save_immediate(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        save_steps = [s for s in data["steps"] if s["type"] == "save_immediate"]
        assert len(save_steps) >= 1

    def test_ends_with_load_level(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        last_step = data["steps"][-1]
        assert last_step["type"] == "load_level"
        assert last_step["level_path"] == "world2/level_2_1"

    def test_has_bep_glow_effect(self):
        """Verify Bep's glow effect is spawned (key story beat)."""
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        spawn_steps = [s for s in data["steps"] if s["type"] == "spawn_effect"]
        tags = {s.get("tag", "") for s in spawn_steps}
        assert "bep_glow" in tags

    def test_has_portal_effect(self):
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        spawn_steps = [s for s in data["steps"] if s["type"] == "spawn_effect"]
        tags = {s.get("tag", "") for s in spawn_steps}
        assert "portal" in tags

    def test_bep_speaks_about_time_travel(self):
        """Verify Bep has dialogue explaining the portal / curse."""
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        bep_lines = [
            s["text"] for s in data["steps"]
            if s.get("type") == "dialogue" and s.get("speaker") == "Bep"
        ]
        assert len(bep_lines) >= 2
        # At least one line should reference the strange feeling or portal.
        combined = " ".join(bep_lines).lower()
        assert "strange" in combined or "portal" in combined or "happening" in combined

    def test_dimoni_explains_curse(self):
        """Verify the Dimoni explains that Bep's curse causes time travel."""
        data = CutsceneScene.load_cutscene_data("post_boss_w1")
        dimoni_lines = [
            s["text"] for s in data["steps"]
            if s.get("type") == "dialogue" and "Dimoni" in s.get("speaker", "")
        ]
        combined = " ".join(dimoni_lines).lower()
        assert "herbs" in combined or "fire" in combined or "sheep" in combined


class TestMainMenuIntroCutsceneIntegration:
    """Tests for the intro cutscene being pushed when starting a new game."""

    def test_start_game_pushes_cutscene_overlay(self):
        """Verify that starting a new game pushes a CutsceneScene overlay."""
        bus = EventBus()
        menu = MainMenuScene(event_bus=bus)
        mgr = SceneManager()
        menu.scene_manager = mgr
        mgr.push(menu)

        # Select Start and confirm.
        menu.handle_input(InputState(move_left=True))  # Ensure on Start.
        menu._selected = MainMenuScene._OPT_START
        menu.handle_input(InputState(jump_pressed=True))
        menu.update(0.016)

        # The top of the stack should be the CutsceneScene overlay.
        assert isinstance(mgr.active_scene, CutsceneScene)
        assert mgr.active_scene.is_overlay is True

    def test_start_game_has_gameplay_underneath(self):
        """Verify GameplayScene is below the cutscene overlay."""
        bus = EventBus()
        menu = MainMenuScene(event_bus=bus)
        mgr = SceneManager()
        menu.scene_manager = mgr
        mgr.push(menu)

        menu._selected = MainMenuScene._OPT_START
        menu.handle_input(InputState(jump_pressed=True))
        menu.update(0.016)

        from sa_fona.scenes.gameplay import GameplayScene

        # Stack should have: [GameplayScene, CutsceneScene]
        assert len(mgr._stack) == 2
        assert isinstance(mgr._stack[0], GameplayScene)
        assert isinstance(mgr._stack[1], CutsceneScene)


class TestMainMenuLevelSelect:
    """Tests for the Level Select option in the main menu."""

    def test_menu_has_three_options(self):
        menu = MainMenuScene()
        assert len(menu._options) == 3
        assert menu._options[2] == "Level Select"

    def test_level_select_option_index(self):
        assert MainMenuScene._OPT_LEVEL_SELECT == 2

    def test_selecting_level_select_opens_scene(self):
        bus = EventBus()
        menu = MainMenuScene(event_bus=bus)
        mgr = SceneManager()
        menu.scene_manager = mgr
        mgr.push(menu)

        menu._selected = MainMenuScene._OPT_LEVEL_SELECT
        menu.handle_input(InputState(jump_pressed=True))
        menu.update(0.016)

        from sa_fona.scenes.level_select import LevelSelectScene
        assert isinstance(mgr.active_scene, LevelSelectScene)
