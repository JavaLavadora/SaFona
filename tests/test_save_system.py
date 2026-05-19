"""Tests for SaveSystem and MainMenuScene."""

import json
import os

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.systems.save_system import SaveSystem


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def bus():
    """Create a fresh EventBus."""
    return EventBus()


@pytest.fixture
def save_path(tmp_path):
    """Return a temporary save file path."""
    return str(tmp_path / "test_save.json")


@pytest.fixture
def save_sys(bus, save_path):
    """Create a SaveSystem with a temp save path."""
    return SaveSystem(bus, save_path=save_path)


# ── Save / Load round-trip ────────────────────────────────────────


class TestSaveLoadRoundTrip:
    """Tests for save and load correctness."""

    def test_save_creates_file(self, save_sys, save_path):
        save_sys.save()
        assert os.path.isfile(save_path)

    def test_save_load_roundtrip(self, save_sys, save_path, bus):
        save_sys.set_level("/some/level.json")
        save_sys.set_player_state(stone_count=42, current_hearts=2.5, max_hearts=4)
        save_sys.save()

        # Load into a fresh instance.
        new_sys = SaveSystem(bus, save_path=save_path)
        data = new_sys.load()

        assert data is not None
        assert data["current_level"] == "/some/level.json"
        assert data["stone_count"] == 42
        assert data["current_hearts"] == 2.5
        assert data["max_hearts"] == 4

    def test_save_contains_version_and_timestamp(self, save_sys, save_path):
        save_sys.save()
        with open(save_path, "r") as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert data["timestamp"] != ""

    def test_load_returns_none_when_no_file(self, bus, tmp_path):
        sys = SaveSystem(bus, save_path=str(tmp_path / "nonexistent.json"))
        assert sys.load() is None

    def test_load_returns_none_on_corrupt_file(self, bus, tmp_path):
        bad_path = str(tmp_path / "bad.json")
        with open(bad_path, "w") as f:
            f.write("not json{{{")
        sys = SaveSystem(bus, save_path=bad_path)
        assert sys.load() is None

    def test_save_creates_directory(self, bus, tmp_path):
        deep_path = str(tmp_path / "sub" / "dir" / "save.json")
        sys = SaveSystem(bus, save_path=deep_path)
        sys.save()
        assert os.path.isfile(deep_path)


# ── exists() ──────────────────────────────────────────────────────


class TestExists:
    """Tests for the exists() method."""

    def test_exists_false_when_no_file(self, save_sys):
        assert save_sys.exists() is False

    def test_exists_true_after_save(self, save_sys):
        save_sys.save()
        assert save_sys.exists() is True

    def test_exists_false_after_delete(self, save_sys):
        save_sys.save()
        save_sys.delete()
        assert save_sys.exists() is False


# ── Death rollback ────────────────────────────────────────────────


class TestDeathRollback:
    """Tests for snapshot/rollback on death."""

    def test_snapshot_captures_state(self, save_sys):
        snap = save_sys.snapshot_level_entry(
            stone_count=50,
            current_hearts=3.0,
            max_hearts=3,
        )
        assert snap["stone_count"] == 50
        assert snap["current_hearts"] == 3.0
        assert snap["max_hearts"] == 3

    def test_rollback_restores_state(self, save_sys):
        # Take snapshot at level entry.
        save_sys.snapshot_level_entry(
            stone_count=50,
            current_hearts=3.0,
            max_hearts=3,
        )
        # Simulate in-level state changes.
        save_sys.set_player_state(
            stone_count=80,
            current_hearts=1.0,
            max_hearts=3,
        )
        assert save_sys.state["stone_count"] == 80

        # Rollback on death.
        snap = save_sys.rollback_to_snapshot()
        assert snap is not None
        assert save_sys.state["stone_count"] == 50
        assert save_sys.state["current_hearts"] == 3.0

    def test_rollback_returns_none_without_snapshot(self, save_sys):
        result = save_sys.rollback_to_snapshot()
        assert result is None

    def test_consumable_refund_on_death(self, save_sys):
        # Take snapshot with 2 ensaimadas.
        save_sys.snapshot_level_entry(
            stone_count=10,
            current_hearts=3.0,
            max_hearts=3,
            consumables={"ensaimada": 2},
        )
        # Player uses one ensaimada during the level.
        save_sys._state["consumables"] = {"ensaimada": 1}

        # Rollback restores to 2.
        snap = save_sys.rollback_to_snapshot()
        assert snap is not None
        assert save_sys.state["consumables"]["ensaimada"] == 2


# ── EventBus integration ─────────────────────────────────────────


class TestEventBusIntegration:
    """Tests for automatic saving on level_complete."""

    def test_level_complete_triggers_save(self, save_sys, save_path, bus):
        save_sys.set_level("/data/levels/world1/level_1_1.json")
        save_sys.set_player_state(stone_count=20, current_hearts=3.0, max_hearts=3)

        bus.publish("level_complete")

        assert os.path.isfile(save_path)
        with open(save_path, "r") as f:
            data = json.load(f)
        assert data["stone_count"] == 20

    def test_cleanup_unsubscribes(self, save_sys, save_path, bus):
        save_sys.cleanup()
        # After cleanup, level_complete should not trigger save.
        save_sys.set_player_state(stone_count=99, current_hearts=3.0, max_hearts=3)
        bus.publish("level_complete")
        assert not os.path.isfile(save_path)


# ── Delete ────────────────────────────────────────────────────────


class TestDelete:
    """Tests for save file deletion."""

    def test_delete_removes_file(self, save_sys, save_path):
        save_sys.save()
        assert os.path.isfile(save_path)
        save_sys.delete()
        assert not os.path.isfile(save_path)

    def test_delete_resets_state(self, save_sys):
        save_sys.set_player_state(stone_count=100, current_hearts=1.0, max_hearts=5)
        save_sys.delete()
        assert save_sys.state["stone_count"] == 0
        assert save_sys.state["max_hearts"] == 3

    def test_delete_clears_snapshot(self, save_sys):
        save_sys.snapshot_level_entry(
            stone_count=10, current_hearts=3.0, max_hearts=3
        )
        save_sys.delete()
        assert save_sys.level_entry_snapshot is None


# ── MainMenuScene ─────────────────────────────────────────────────


class TestMainMenuScene:
    """Tests for MainMenuScene behavior."""

    @pytest.fixture(autouse=True)
    def init_pygame(self):
        """Ensure pygame is initialized for font rendering."""
        pygame.init()
        yield
        # Don't quit pygame here as other tests may need it.

    def test_continue_disabled_when_no_save(self, bus, save_path):
        from sa_fona.scenes.main_menu import MainMenuScene

        sys = SaveSystem(bus, save_path=save_path)
        menu = MainMenuScene(event_bus=bus, save_system=sys)
        menu.on_enter()

        assert menu.has_save is False
        # Default selection should be Start when no save exists.
        assert menu.selected == 0  # _OPT_START

    def test_continue_enabled_when_save_exists(self, bus, save_path):
        from sa_fona.scenes.main_menu import MainMenuScene

        sys = SaveSystem(bus, save_path=save_path)
        sys.save()  # Create save file.

        menu = MainMenuScene(event_bus=bus, save_system=sys)
        menu.on_enter()

        assert menu.has_save is True
        # Default selection should be Continue when save exists.
        assert menu.selected == 1  # _OPT_CONTINUE

    def test_cannot_select_continue_when_disabled(self, bus, save_path):
        from sa_fona.core.input_handler import InputState
        from sa_fona.scenes.main_menu import MainMenuScene

        sys = SaveSystem(bus, save_path=save_path)
        menu = MainMenuScene(event_bus=bus, save_system=sys)
        menu.on_enter()

        # Try to move right — Continue is disabled, so it should skip
        # over it and land on Level Select (index 2).
        inp = InputState(move_right=True)
        menu.handle_input(inp)

        assert menu.selected == MainMenuScene._OPT_LEVEL_SELECT

        # Moving left should skip back over Continue to Start.
        inp = InputState(move_left=True)
        menu.handle_input(inp)
        assert menu.selected == MainMenuScene._OPT_START

    def test_menu_renders_without_crash(self, bus, save_path):
        from sa_fona.scenes.main_menu import MainMenuScene

        sys = SaveSystem(bus, save_path=save_path)
        menu = MainMenuScene(event_bus=bus, save_system=sys)
        menu.on_enter()

        surface = pygame.Surface((384, 216))
        menu.render(surface)  # Should not raise.
