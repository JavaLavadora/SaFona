"""Main Game class for Sa Fona.

Owns the Pygame window, the main loop, and top-level subsystem
references (input, events, scenes).  The loop processes events,
updates game state, renders to the internal surface, and presents
the scaled result at 60 FPS.
"""

from __future__ import annotations

import json
import sys

import pygame

from sa_fona.config.settings import (
    BASE_HEIGHT,
    BASE_WIDTH,
    COLORS,
    DATA_DIR,
    FPS,
    GAME_TITLE,
    WINDOW_SCALE,
)
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputHandler
from sa_fona.core.scene_manager import SceneManager
from sa_fona.rendering.pixel_scaler import PixelScaler
from sa_fona.rendering.sprite_renderer import SpriteRenderer
from sa_fona.scenes.gameplay import GameplayScene
from sa_fona.scenes.main_menu import MainMenuScene
from sa_fona.systems.save_system import SaveSystem


class Game:
    """Top-level game object.

    Creates the Pygame window, initialises subsystems, and runs
    the main loop.

    Attributes:
        display: The OS-level display surface (scaled window).
        scaler: The PixelScaler that manages the internal render surface.
        clock: Pygame clock used for frame-rate limiting.
        running: Whether the main loop should continue.
        input_handler: Processes raw input into action state.
        event_bus: Broadcasts game events to listeners.
        scene_manager: Manages the active scene stack.
        sprite_renderer: Generates and caches placeholder sprite surfaces.
    """

    def __init__(
        self,
        level_path: str | None = None,
        skip_menu: bool = False,
    ) -> None:
        """Initialise Pygame and create the game window.

        Args:
            level_path: Optional explicit path to a level JSON file.
                If ``None``, tries World 1 Level 1, then falls back to
                the test level.
            skip_menu: If True, bypass the main menu and load gameplay
                directly (used by --level and --boss CLI flags).
        """
        pygame.init()

        window_width = BASE_WIDTH * WINDOW_SCALE
        window_height = BASE_HEIGHT * WINDOW_SCALE

        self.display: pygame.Surface = pygame.display.set_mode(
            (window_width, window_height)
        )
        pygame.display.set_caption(GAME_TITLE)

        self.scaler = PixelScaler()
        self.clock = pygame.time.Clock()
        self.running: bool = True

        # Core systems.
        controls_path = str(DATA_DIR / "controls_default.json")
        self.input_handler = InputHandler(controls_path)
        self.event_bus = EventBus()
        self.scene_manager = SceneManager()

        # Save system (single slot).
        self.save_system = SaveSystem(self.event_bus)

        # Load asset manifest and create sprite renderer.
        manifest_path = DATA_DIR / "asset_manifest.json"
        with open(manifest_path, "r", encoding="utf-8") as fh:
            full_manifest = json.load(fh)
        self.sprite_renderer = SpriteRenderer(full_manifest.get("sprites", {}))

        if skip_menu:
            # Bypass menu: load gameplay directly (for --level / --boss).
            if level_path is None:
                level_path = self._resolve_starting_level()

            gameplay_scene = GameplayScene(
                BASE_WIDTH, BASE_HEIGHT, event_bus=self.event_bus,
                level_path=level_path,
            )
            gameplay_scene.scene_manager = self.scene_manager
            gameplay_scene.save_system = self.save_system
            gameplay_scene.take_level_entry_snapshot()
            self.scene_manager.push(gameplay_scene)
        else:
            # Show main menu.
            menu_scene = MainMenuScene(
                BASE_WIDTH, BASE_HEIGHT,
                event_bus=self.event_bus,
                save_system=self.save_system,
            )
            menu_scene.scene_manager = self.scene_manager
            self.scene_manager.push(menu_scene)

        self._print_display_info(window_width, window_height)

    # ── Public API ──────────────────────────────────────────────

    def run(self) -> None:
        """Execute the main game loop.

        Processes events, updates game state, and renders at the
        target frame rate until the user quits.
        """
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # seconds
            self._process_events()
            self._update(dt)
            self._render()

        pygame.quit()

    # ── Private helpers ─────────────────────────────────────────

    def _process_events(self) -> None:
        """Pump the Pygame event queue and dispatch to subsystems."""
        events = pygame.event.get()

        # Check for window close.
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

        # Process input through the input handler.
        input_state = self.input_handler.process_events(events)

        # Let the active scene handle input.
        if not self.scene_manager.is_empty:
            self.scene_manager.active_scene.handle_input(input_state)

            # Check if the active scene wants to quit.
            active = self.scene_manager.active_scene
            if hasattr(active, "quit_requested") and active.quit_requested:
                active.quit_requested = False
                if isinstance(active, MainMenuScene):
                    self.running = False
                else:
                    self._return_to_menu()

    def _return_to_menu(self) -> None:
        """Replace the current scene with the main menu."""
        active = self.scene_manager.active_scene
        if hasattr(active, "on_exit"):
            active.on_exit()
        menu = MainMenuScene(
            BASE_WIDTH, BASE_HEIGHT,
            event_bus=self.event_bus,
            save_system=self.save_system,
        )
        menu.scene_manager = self.scene_manager
        self.scene_manager.replace(menu)

    def _update(self, dt: float) -> None:
        """Advance game state by dt seconds.

        Args:
            dt: Elapsed time since the previous frame, in seconds.
        """
        self.scene_manager.update(dt)

    def _render(self) -> None:
        """Draw the current frame and present it."""
        surface = self.scaler.get_surface()
        surface.fill(COLORS["BLACK"])
        self.scene_manager.render(surface)
        self.scaler.present(self.display)
        pygame.display.flip()

    @staticmethod
    def _resolve_starting_level() -> str | None:
        """Find the best starting level.

        Prefers World 1 Level 1 if it exists, otherwise falls back to the
        test level. Returns ``None`` when no level file is found (the
        GameplayScene will then use its own default).

        Returns:
            Filesystem path to the level JSON, or ``None``.
        """
        w1_l1 = DATA_DIR / "levels" / "world1" / "level_1_1.json"
        if w1_l1.exists():
            return str(w1_l1)
        test_level = DATA_DIR / "levels" / "test" / "test_level.json"
        if test_level.exists():
            return str(test_level)
        return None

    @staticmethod
    def _print_display_info(width: int, height: int) -> None:
        """Print connection info for users on a code tunnel.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
        """
        print("=" * 50)
        print(f"  {GAME_TITLE}")
        print(f"  Window : {width}x{height}")
        print(f"  Native : {BASE_WIDTH}x{BASE_HEIGHT}")
        print(f"  Scale  : {WINDOW_SCALE}x")
        print(f"  FPS    : {FPS}")
        driver = pygame.display.get_driver()
        print(f"  Driver : {driver}")
        print("=" * 50)
        sys.stdout.flush()
