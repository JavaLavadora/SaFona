"""Level select scene: browse and load any available level.

Scans the data/levels/ directory for world sub-directories and level
JSON files, presents them in a navigable list, and loads the chosen
level into a GameplayScene. Also discovers boss encounters from
data/bosses/ and includes them after the last regular level of each world.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH, DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.save_system import SaveSystem


# ── Colors (consistent with main menu) ───────────────────────────
_BG_COLOR: tuple[int, int, int] = (20, 20, 40)
_TITLE_COLOR: tuple[int, int, int] = (255, 220, 80)
_OPTION_COLOR: tuple[int, int, int] = (240, 240, 240)
_SELECTED_COLOR: tuple[int, int, int] = (255, 180, 50)
_BACK_COLOR: tuple[int, int, int] = (200, 200, 200)


def discover_levels() -> list[dict[str, str]]:
    """Scan the levels directory and return an ordered list of levels.

    Each entry is a dict with:
        - display_name: Human-readable name (e.g. "World 1 - Level 1").
        - level_path: Absolute path to the level JSON file.
        - world: World identifier (e.g. "world1").

    Returns:
        Sorted list of level dicts. Test levels are placed at the end.
    """
    levels_dir = DATA_DIR / "levels"
    if not levels_dir.is_dir():
        return []

    results: list[dict[str, str]] = []

    for world_dir in sorted(levels_dir.iterdir()):
        if not world_dir.is_dir():
            continue

        world_name = world_dir.name  # e.g. "world1", "test"

        for level_file in sorted(world_dir.glob("*.json")):
            stem = level_file.stem  # e.g. "level_1_1"

            # Build a friendly display name.
            if world_name == "test":
                display_name = f"Test - {stem.replace('_', ' ').title()}"
            else:
                # Parse "worldN" -> "World N"
                world_num = world_name.replace("world", "")
                # Parse "level_N_M" -> "Level M"
                parts = stem.split("_")
                if len(parts) >= 3:
                    level_num = parts[2]
                    display_name = f"World {world_num} - Level {level_num}"
                else:
                    display_name = f"World {world_num} - {stem}"

            results.append({
                "display_name": display_name,
                "level_path": str(level_file),
                "world": world_name,
            })

    # Sort: numbered worlds first (numerically), then test.
    def sort_key(entry: dict[str, str]) -> tuple[int, int, str]:
        world = entry["world"]
        if world == "test":
            return (999, 0, entry["display_name"])
        # Extract number from "World N" for numeric sort.
        match = re.search(r"(\d+)", world)
        world_num = int(match.group(1)) if match else 0
        # Extract level number from display name.
        match2 = re.search(r"(\d+)", entry["display_name"].split("-")[-1])
        level_num = int(match2.group(1)) if match2 else 0
        return (world_num, level_num, entry["display_name"])

    results.sort(key=sort_key)

    # Discover boss encounters from data/bosses/ and insert them after the
    # last regular level of their world.
    bosses_dir = DATA_DIR / "bosses"
    if bosses_dir.is_dir():
        boss_entries: list[dict[str, str]] = []
        for boss_file in sorted(bosses_dir.glob("*.json")):
            try:
                with open(boss_file, "r", encoding="utf-8") as fh:
                    boss_def = json.load(fh)
            except (json.JSONDecodeError, OSError):
                continue

            boss_id = boss_def.get("boss_id", boss_file.stem)
            display_name_raw = boss_def.get("display_name", boss_id)
            world_num = boss_def.get("world", 0)
            world_key = f"world{world_num}"
            cutscene_id = boss_def.get("post_defeat", {}).get(
                "cutscene", "post_boss_w1"
            )
            display_name = f"World {world_num} - Boss: {display_name_raw}"

            boss_entries.append({
                "display_name": display_name,
                "level_path": "",  # Empty — bosses are procedural.
                "world": world_key,
                "boss_id": boss_id,
                "cutscene_id": cutscene_id,
            })

        # Insert each boss entry after the last regular level of its world.
        for boss in boss_entries:
            boss_world = boss["world"]
            insert_idx = len(results)
            for i, entry in enumerate(results):
                if entry["world"] == boss_world:
                    insert_idx = i + 1
            results.insert(insert_idx, boss)

    return results


class LevelSelectScene(BaseScene):
    """Scene that lists available levels for direct selection.

    Navigates with left/right (mapped to up/down in the list since the
    InputState provides move_left/move_right as primary directional input).
    Jump or interact confirms selection. Pause (ESC) returns to the main
    menu. A "Back" entry at the top of the list also returns to the menu.

    Args:
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
        event_bus: Shared event bus for cross-system communication.
        save_system: Optional save system to wire into gameplay.
    """

    def __init__(
        self,
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
        event_bus: EventBus | None = None,
        save_system: SaveSystem | None = None,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._event_bus = event_bus or EventBus()
        self._save_system = save_system

        # Discover available levels.
        self._levels = discover_levels()

        # Entries: "Back" + all discovered levels.
        self._entries: list[str] = ["< Back"] + [
            lvl["display_name"] for lvl in self._levels
        ]

        self._selected: int = 1 if self._levels else 0

        # Previous-frame directional input state for edge detection.
        self._prev_left: bool = False
        self._prev_right: bool = False
        self._prev_down: bool = False

        # Deferred action.
        self._pending_action: str | None = None

        # Scene manager (set externally).
        self._scene_manager = None

        # Fonts (lazy init).
        self._title_font: pygame.font.Font | None = None
        self._option_font: pygame.font.Font | None = None

        # Quit flag.
        self.quit_requested: bool = False

    # ── Properties ────────────────────────────────────────────────

    @property
    def selected(self) -> int:
        """Currently selected entry index."""
        return self._selected

    @property
    def levels(self) -> list[dict[str, str]]:
        """List of discovered level dicts."""
        return self._levels

    @property
    def entries(self) -> list[str]:
        """Full list of display entries including Back."""
        return self._entries

    @property
    def scene_manager(self):
        """Scene manager reference."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value) -> None:
        self._scene_manager = value

    # ── Scene lifecycle ───────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered."""

    def on_exit(self) -> None:
        """Scene exited."""

    def handle_input(self, input_state: InputState) -> None:
        """Navigate the level list and confirm selection.

        Uses move_left for previous (up) and move_right for next (down),
        matching the main menu navigation style.  Also supports move_down
        for scrolling down if available.  Jump or interact confirms.

        Args:
            input_state: Current frame input snapshot.
        """
        # Navigate: left = up, right/down = down.
        # Edge detection: only move on the frame the key is first pressed.
        left_pressed = input_state.move_left and not self._prev_left
        right_pressed = input_state.move_right and not self._prev_right
        down_pressed = input_state.move_down and not self._prev_down
        self._prev_left = input_state.move_left
        self._prev_right = input_state.move_right
        self._prev_down = input_state.move_down

        if left_pressed:
            self._selected = max(0, self._selected - 1)
        elif right_pressed or down_pressed:
            self._selected = min(len(self._entries) - 1, self._selected + 1)

        # Confirm selection.
        if input_state.jump_pressed or input_state.interact_pressed:
            if self._selected == 0:
                self._pending_action = "back"
            else:
                self._pending_action = "select"

        # ESC returns to main menu.
        if input_state.pause_pressed:
            self._pending_action = "back"

    def update(self, dt: float) -> None:
        """Process deferred actions.

        Args:
            dt: Delta time in seconds.
        """
        if self._pending_action == "back":
            self._pending_action = None
            self._go_back()
        elif self._pending_action == "select":
            self._pending_action = None
            self._select_level()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the level select list.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill(_BG_COLOR)

        # Lazy font init.
        if self._title_font is None:
            try:
                self._title_font = pygame.font.Font(None, 24)
            except Exception:
                self._title_font = None

        if self._option_font is None:
            try:
                self._option_font = pygame.font.Font(None, 16)
            except Exception:
                self._option_font = None

        # Title.
        if self._title_font is not None:
            title = self._title_font.render("Level Select", False, _TITLE_COLOR)
            tx = (self._screen_width - title.get_width()) // 2
            surface.blit(title, (tx, 12))

        # Level list.
        if self._option_font is None:
            return

        line_height = 18
        # Calculate visible area (leave space for title).
        start_y = 40
        max_visible = (self._screen_height - start_y - 10) // line_height

        # Scroll offset to keep selected item visible.
        scroll_offset = 0
        if self._selected >= max_visible:
            scroll_offset = self._selected - max_visible + 1

        for i in range(scroll_offset, min(len(self._entries), scroll_offset + max_visible)):
            entry = self._entries[i]

            # Color based on type and selection state.
            if i == self._selected:
                color = _SELECTED_COLOR
            elif i == 0:
                color = _BACK_COLOR
            else:
                color = _OPTION_COLOR

            text_surf = self._option_font.render(entry, False, color)
            oy = start_y + (i - scroll_offset) * line_height
            ox = (self._screen_width - text_surf.get_width()) // 2

            surface.blit(text_surf, (ox, oy))

            # Draw cursor arrow for selected entry.
            if i == self._selected:
                arrow = self._option_font.render(">", False, _SELECTED_COLOR)
                surface.blit(arrow, (ox - 14, oy))

    # ── Actions ───────────────────────────────────────────────────

    def _go_back(self) -> None:
        """Return to the main menu."""
        if self._scene_manager is None:
            return

        from sa_fona.scenes.main_menu import MainMenuScene

        menu = MainMenuScene(
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            event_bus=self._event_bus,
            save_system=self._save_system,
        )
        menu.scene_manager = self._scene_manager
        self._scene_manager.replace(menu)

    def _select_level(self) -> None:
        """Load the selected level into a GameplayScene or BossScene."""
        if self._scene_manager is None:
            return

        # Index into _levels is offset by 1 (index 0 is "Back").
        level_idx = self._selected - 1
        if level_idx < 0 or level_idx >= len(self._levels):
            return

        level_info = self._levels[level_idx]

        # Boss entries have a boss_id key — launch BossScene instead.
        if level_info.get("boss_id"):
            self._select_boss(level_info)
            return

        level_path = level_info["level_path"]

        if not Path(level_path).is_file():
            return

        from sa_fona.scenes.gameplay import GameplayScene

        scene = GameplayScene(
            self._screen_width,
            self._screen_height,
            event_bus=self._event_bus,
            level_path=level_path,
        )
        scene.scene_manager = self._scene_manager

        if self._save_system is not None:
            scene.save_system = self._save_system
            scene.take_level_entry_snapshot()

        self._scene_manager.replace(scene)

    def _select_boss(self, boss_info: dict[str, str]) -> None:
        """Load the selected boss encounter into a BossScene.

        Args:
            boss_info: Dict with boss_id, cutscene_id, and other metadata.
        """
        if self._scene_manager is None:
            return

        from sa_fona.scenes.boss_scene import BossScene

        scene = BossScene(
            boss_id=boss_info["boss_id"],
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            event_bus=self._event_bus,
            cutscene_id=boss_info.get("cutscene_id", "post_boss_w1"),
            on_load_level=self._make_load_level_cb(),
        )
        scene.scene_manager = self._scene_manager
        self._scene_manager.replace(scene)

    def _make_load_level_cb(self) -> callable:
        """Create a callback for the post-boss cutscene to load the next level.

        When the boss is defeated and the cutscene reaches a load_level
        step, this callback creates a new GameplayScene for the target
        level and replaces the current scene.

        Subscribes to mask_acquired on the EventBus so masks granted
        during the cutscene are captured and propagated to the new scene.

        Returns:
            A callable accepting a level_path string (relative to
            data/levels/, e.g. "world2/level_2_1").
        """
        scene_mgr = self._scene_manager
        event_bus = self._event_bus
        save_sys = self._save_system
        screen_w = self._screen_width
        screen_h = self._screen_height
        acquired_masks: list[str] = []

        def _on_mask(mask_id: str = "", **kwargs: object) -> None:
            acquired_masks.append(mask_id)

        event_bus.subscribe("mask_acquired", _on_mask)

        def _load(level_path: str) -> None:
            try:
                event_bus.unsubscribe("mask_acquired", _on_mask)
            except ValueError:
                pass
            full_path = str(DATA_DIR / "levels" / f"{level_path}.json")
            if not Path(full_path).is_file():
                return

            from sa_fona.scenes.gameplay import GameplayScene

            new_scene = GameplayScene(
                screen_w, screen_h,
                event_bus=event_bus,
                level_path=full_path,
            )
            new_scene.scene_manager = scene_mgr
            for mask_id in acquired_masks:
                new_scene.mask_system.unlock_mask(mask_id)
                new_scene.mask_system.equip_mask(mask_id)
            if save_sys is not None:
                new_scene.save_system = save_sys
                mask_state = new_scene.mask_system.get_save_state()
                save_sys.state["masks_unlocked"] = mask_state["unlocked_masks"]
                save_sys.state["masks_equipped"] = (
                    [mask_state["equipped_mask"]]
                    if mask_state["equipped_mask"] else []
                )
                save_sys.save()
                new_scene.take_level_entry_snapshot()
            scene_mgr.replace(new_scene)

        return _load
