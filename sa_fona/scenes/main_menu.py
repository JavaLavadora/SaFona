"""Main menu scene: title screen with Start, Continue, and Level Select options.

Displays the title image (assets/ui/title.png) centered on screen,
three menu options, and an arrow cursor.  Falls back to text rendering
when the title image is missing.
The Continue option is grayed out when no save file exists.
"""

from __future__ import annotations

from pathlib import Path

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.rendering.asset_loader import load_ui_asset
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.save_system import SaveSystem


# ── Colors ─────────────────────────────────────────────────────────
_BG_COLOR: tuple[int, int, int] = (20, 20, 40)
_TITLE_COLOR: tuple[int, int, int] = (255, 220, 80)
_OPTION_COLOR: tuple[int, int, int] = (240, 240, 240)
_OPTION_DISABLED_COLOR: tuple[int, int, int] = (80, 80, 80)
_CURSOR_COLOR: tuple[int, int, int] = (255, 180, 50)
_SUBTITLE_COLOR: tuple[int, int, int] = (150, 150, 180)


class MainMenuScene(BaseScene):
    """Title screen with Start, Continue, and Level Select options.

    Arrow keys navigate, Space or Enter confirms.  The Continue option
    is disabled (grayed out) when no save file exists.

    Args:
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
        event_bus: Shared event bus for cross-system communication.
        save_system: The save system used to check for existing saves.
    """

    # Menu option indices.
    _OPT_START = 0
    _OPT_CONTINUE = 1
    _OPT_LEVEL_SELECT = 2

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

        # Save system for checking if a save exists.
        self._save_system = save_system

        # Menu state.
        self._selected: int = self._OPT_START
        self._options: list[str] = ["Start", "Continue", "Level Select"]
        self._has_save: bool = (
            self._save_system.exists() if self._save_system is not None else False
        )

        # Deferred action to execute after update.
        self._pending_action: str | None = None

        # Scene manager (set externally).
        self._scene_manager = None

        # Fonts (lazy init).
        self._title_font: pygame.font.Font | None = None
        self._option_font: pygame.font.Font | None = None
        self._subtitle_font: pygame.font.Font | None = None

        # Quit flag.
        self.quit_requested: bool = False

        # Title image (loaded lazily).
        self._title_image: pygame.Surface | None = None
        self._title_image_loaded: bool = False

    # ── Properties ────────────────────────────────────────────────

    @property
    def selected(self) -> int:
        """Currently selected menu option index."""
        return self._selected

    @property
    def has_save(self) -> bool:
        """Whether a save file exists (Continue is enabled)."""
        return self._has_save

    @property
    def scene_manager(self):
        """Scene manager reference."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value) -> None:
        self._scene_manager = value

    # ── Scene lifecycle ───────────────────────────────────────────

    def on_enter(self) -> None:
        """Refresh save-exists check on scene entry."""
        self._has_save = (
            self._save_system.exists() if self._save_system is not None else False
        )
        # Default selection: Start if no save, otherwise Continue.
        if self._has_save:
            self._selected = self._OPT_CONTINUE
        else:
            self._selected = self._OPT_START

    def on_exit(self) -> None:
        """Clean up when leaving the menu."""

    def handle_input(self, input_state: InputState) -> None:
        """Navigate menu and confirm selection.

        Uses left/right arrows to move the cursor between the two menu
        options (since the InputState provides ``move_left`` / ``move_right``
        for directional input). Jump (Space) or interact (Enter) confirms.

        Args:
            input_state: Current frame input snapshot.
        """
        # Navigate: left = previous option, right = next option.
        if input_state.move_left:
            self._move_selection(-1)
        elif input_state.move_right:
            self._move_selection(1)

        # Confirm selection with jump (Space) or interact (Enter).
        if input_state.jump_pressed or input_state.interact_pressed:
            self._confirm_selection()

    def _move_selection(self, direction: int) -> None:
        """Move the menu cursor, skipping disabled options.

        Args:
            direction: -1 for previous, +1 for next.
        """
        new_sel = self._selected + direction
        new_sel = max(0, min(len(self._options) - 1, new_sel))
        # Skip disabled options in the same direction.
        if new_sel == self._OPT_CONTINUE and not self._has_save:
            new_sel += direction
            new_sel = max(0, min(len(self._options) - 1, new_sel))
        self._selected = new_sel

    def _confirm_selection(self) -> None:
        """Execute the currently selected menu option (deferred)."""
        if self._selected == self._OPT_START:
            self._pending_action = "start"
        elif self._selected == self._OPT_CONTINUE and self._has_save:
            self._pending_action = "continue"
        elif self._selected == self._OPT_LEVEL_SELECT:
            self._pending_action = "level_select"

    def update(self, dt: float) -> None:
        """Process deferred actions.

        Args:
            dt: Delta time in seconds.
        """
        if self._pending_action == "start":
            self._pending_action = None
            self._start_new_game()
        elif self._pending_action == "continue":
            self._pending_action = None
            self._continue_game()
        elif self._pending_action == "level_select":
            self._pending_action = None
            self._open_level_select()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the main menu.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill(_BG_COLOR)

        # Lazy font init.
        if self._title_font is None:
            try:
                self._title_font = pygame.font.Font(None, 36)
            except Exception:
                self._title_font = None

        if self._option_font is None:
            try:
                self._option_font = pygame.font.Font(None, 18)
            except Exception:
                self._option_font = None

        if self._subtitle_font is None:
            try:
                self._subtitle_font = pygame.font.Font(None, 12)
            except Exception:
                self._subtitle_font = None

        # Title image or text fallback.
        if not self._title_image_loaded:
            self._title_image = load_ui_asset("title")
            self._title_image_loaded = True

        if self._title_image is not None:
            tx = (self._screen_width - self._title_image.get_width()) // 2
            ty = self._screen_height // 4 - self._title_image.get_height() // 2
            surface.blit(self._title_image, (tx, ty))
        elif self._title_font is not None:
            title = self._title_font.render("Sa Fona", False, _TITLE_COLOR)
            tx = (self._screen_width - title.get_width()) // 2
            ty = self._screen_height // 4
            surface.blit(title, (tx, ty))

        # Subtitle (shown below the title image or text).
        if self._subtitle_font is not None:
            sub = self._subtitle_font.render(
                "A Balearic Adventure", False, _SUBTITLE_COLOR
            )
            sx = (self._screen_width - sub.get_width()) // 2
            sy = self._screen_height // 4 + 30
            surface.blit(sub, (sx, sy))

        # Menu options.
        if self._option_font is not None:
            base_y = self._screen_height * 3 // 5
            line_height = 22

            for i, option_text in enumerate(self._options):
                # Determine color.
                if i == self._OPT_CONTINUE and not self._has_save:
                    color = _OPTION_DISABLED_COLOR
                elif i == self._selected:
                    color = _CURSOR_COLOR
                else:
                    color = _OPTION_COLOR

                text_surf = self._option_font.render(option_text, False, color)
                ox = (self._screen_width - text_surf.get_width()) // 2
                oy = base_y + i * line_height
                surface.blit(text_surf, (ox, oy))

                # Draw cursor arrow for selected option.
                if i == self._selected:
                    arrow = self._option_font.render(">", False, _CURSOR_COLOR)
                    surface.blit(arrow, (ox - 16, oy))

    # ── Actions ───────────────────────────────────────────────────

    def _start_new_game(self) -> None:
        """Start a new game from W1-L1 with an intro cutscene overlay."""
        if self._scene_manager is None:
            return

        from sa_fona.config.settings import DATA_DIR
        from sa_fona.scenes.cutscene import CutsceneScene
        from sa_fona.scenes.gameplay import GameplayScene

        # Delete existing save for a fresh start.
        if self._save_system is not None:
            self._save_system.delete()

        # Find starting level.
        level_path = self._resolve_starting_level()

        scene = GameplayScene(
            self._screen_width,
            self._screen_height,
            event_bus=self._event_bus,
            level_path=level_path,
        )
        scene.scene_manager = self._scene_manager

        # Wire up SaveSystem to the gameplay scene.
        if self._save_system is not None:
            scene.save_system = self._save_system
            scene.take_level_entry_snapshot()

        self._scene_manager.replace(scene)

        # Push the intro cutscene as an overlay on top of gameplay.
        # When the cutscene completes, it auto-pops and reveals gameplay.
        cutscene_data = CutsceneScene.load_cutscene_data("intro")
        if cutscene_data.get("steps"):
            cutscene = CutsceneScene(cutscene_data, self._event_bus)
            cutscene.scene_manager = self._scene_manager
            self._scene_manager.push(cutscene)

    def _continue_game(self) -> None:
        """Continue from the saved state."""
        if self._scene_manager is None or self._save_system is None:
            return

        save_data = self._save_system.load()
        if save_data is None:
            return

        level_path = save_data.get("current_level", "")

        # Fall back to the starting level when the saved path is missing
        # or the file no longer exists on disk.
        if not level_path or not Path(level_path).is_file():
            level_path = self._resolve_starting_level()

        from sa_fona.scenes.gameplay import GameplayScene

        scene = GameplayScene(
            self._screen_width,
            self._screen_height,
            event_bus=self._event_bus,
            level_path=level_path,
        )
        scene.scene_manager = self._scene_manager
        scene.save_system = self._save_system

        # Restore economy state from save.
        stone_count = save_data.get("stone_count", 0)
        scene.economy.add_stones(stone_count)

        # Restore hearts.
        max_hearts = save_data.get("max_hearts", 3)
        current_hearts = save_data.get("current_hearts", float(max_hearts))
        scene.combat.set_player_health(current_hearts, max_hearts)
        scene.hud.set_state(
            max_hearts=max_hearts,
            current_hearts=current_hearts,
            stone_count=stone_count,
        )

        # Restore mask state.
        unlocked = save_data.get("masks_unlocked", [])
        equipped_list = save_data.get("masks_equipped", [])
        equipped = equipped_list[0] if equipped_list else ""
        scene.mask_system.restore_save_state({
            "unlocked_masks": unlocked,
            "equipped_mask": equipped,
        })

        # Restore mid-level checkpoint position.
        cp_x = save_data.get("checkpoint_x")
        cp_y = save_data.get("checkpoint_y")
        if cp_x is not None and cp_y is not None:
            scene._checkpoint_pos = (float(cp_x), float(cp_y))
            scene._player.rect.x = int(cp_x)
            scene._player.rect.y = int(cp_y)

        scene.take_level_entry_snapshot()

        self._scene_manager.replace(scene)

    def _open_level_select(self) -> None:
        """Open the level select scene."""
        if self._scene_manager is None:
            return

        from sa_fona.scenes.level_select import LevelSelectScene

        scene = LevelSelectScene(
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            event_bus=self._event_bus,
            save_system=self._save_system,
        )
        scene.scene_manager = self._scene_manager
        self._scene_manager.replace(scene)

    @staticmethod
    def _resolve_starting_level() -> str | None:
        """Find the best starting level path.

        Returns:
            Path to W1-L1 or test level, or ``None``.
        """
        from sa_fona.config.settings import DATA_DIR

        w1_l1 = DATA_DIR / "levels" / "world1" / "level_1_1.json"
        if w1_l1.exists():
            return str(w1_l1)
        test_level = DATA_DIR / "levels" / "test" / "test_level.json"
        if test_level.exists():
            return str(test_level)
        return None
