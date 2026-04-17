"""Main Game class for Sa Fona.

Owns the Pygame window, the main loop, and top-level subsystem
references (input, events, scenes).  The loop processes events,
updates game state, renders to the internal surface, and presents
the scaled result at 60 FPS.
"""

from __future__ import annotations

import sys

import pygame

from sa_fona.config.settings import (
    BASE_HEIGHT,
    BASE_WIDTH,
    COLORS,
    FPS,
    GAME_TITLE,
    WINDOW_SCALE,
)
from sa_fona.rendering.pixel_scaler import PixelScaler

# ── Graceful imports for subsystems built by N'Andreu-B ──────────
# These modules may not exist yet; fall back to lightweight stubs
# so the game loop can run standalone during early integration.

try:
    from sa_fona.core.input_handler import InputHandler  # type: ignore[import-not-found]
except ImportError:

    class InputHandler:  # type: ignore[no-redef]
        """Stub input handler until the real module lands."""

        def process_event(self, event: pygame.event.Event) -> None:
            """No-op event processing."""

        def update(self) -> None:
            """No-op update."""


try:
    from sa_fona.core.event_bus import EventBus  # type: ignore[import-not-found]
except ImportError:

    class EventBus:  # type: ignore[no-redef]
        """Stub event bus until the real module lands."""

        def emit(self, event_type: str, **kwargs: object) -> None:
            """No-op emit."""


try:
    from sa_fona.core.scene_manager import SceneManager  # type: ignore[import-not-found]
except ImportError:

    class SceneManager:  # type: ignore[no-redef]
        """Stub scene manager until the real module lands."""

        def update(self, dt: float) -> None:
            """No-op update."""

        def render(self, surface: pygame.Surface) -> None:
            """No-op render."""


class Game:
    """Top-level game object.

    Creates the Pygame window, initialises subsystems, and runs
    the main loop.

    Attributes:
        display: The OS-level display surface (scaled window).
        scaler: The :class:`PixelScaler` that manages the internal
            render surface.
        clock: Pygame clock used for frame-rate limiting.
        running: Whether the main loop should continue.
        input_handler: Processes raw input into action state.
        event_bus: Broadcasts game events to listeners.
        scene_manager: Manages the active scene stack.
    """

    def __init__(self) -> None:
        """Initialise Pygame and create the game window."""
        pygame.init()

        window_width = BASE_WIDTH * WINDOW_SCALE
        window_height = BASE_HEIGHT * WINDOW_SCALE

        self.display: pygame.Surface = pygame.display.set_mode(
            (window_width, window_height)
        )
        pygame.display.set_caption(GAME_TITLE)

        self.scaler = PixelScaler()
        self.clock = pygame.Clock()
        self.running: bool = True

        # Subsystems (stubs if the real implementations aren't available)
        self.input_handler = InputHandler()
        self.event_bus = EventBus()
        self.scene_manager = SceneManager()

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
        """Pump the Pygame event queue and dispatch events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.input_handler.process_event(event)

    def _update(self, dt: float) -> None:
        """Advance game state by *dt* seconds.

        Args:
            dt: Elapsed time since the previous frame, in seconds.
        """
        self.input_handler.update()
        self.scene_manager.update(dt)

    def _render(self) -> None:
        """Draw the current frame and present it."""
        surface = self.scaler.get_surface()
        surface.fill(COLORS["BLACK"])
        self.scene_manager.render(surface)
        self.scaler.present(self.display)
        pygame.display.flip()

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
