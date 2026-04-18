"""Heads-up display: hearts, stone count, and future mask icon.

The HUD renders on top of everything in screen space (not affected by
camera offset).  It subscribes to EventBus events to stay in sync with
game state without directly referencing entity or system objects.

Placeholder rendering uses simple geometric shapes:
- Hearts: red filled/half/empty heart shapes (top-left)
- Stone count: grey circle icon + number text (top-right)
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_WIDTH
from sa_fona.core.event_bus import EventBus


# ── Layout constants ──────────────────────────────────────────────
_HEART_SIZE: int = 12
_HEART_SPACING: int = 2
_HEART_MARGIN_X: int = 4
_HEART_MARGIN_Y: int = 4

_STONE_MARGIN_X: int = 4
_STONE_MARGIN_Y: int = 4
_STONE_ICON_RADIUS: int = 5
_STONE_TEXT_OFFSET_X: int = 14

# Colors.
_HEART_FULL_COLOR: tuple[int, int, int] = (220, 40, 40)
_HEART_HALF_COLOR: tuple[int, int, int] = (220, 120, 120)
_HEART_EMPTY_COLOR: tuple[int, int, int] = (80, 40, 40)
_STONE_ICON_COLOR: tuple[int, int, int] = (160, 160, 160)
_STONE_TEXT_COLOR: tuple[int, int, int] = (220, 220, 220)
_STONE_TEXT_SHADOW: tuple[int, int, int] = (40, 40, 40)


class HUD:
    """In-game heads-up display.

    Displays player health (hearts) and stone count.  Updates are
    driven by EventBus subscriptions, keeping the HUD decoupled from
    the Player entity and EconomySystem.

    Args:
        event_bus: Shared event bus for receiving game events.
        max_hearts: Maximum number of hearts (default 3).
        current_hearts: Starting heart count (default 3.0).
        stone_count: Starting stone count (default 0).
    """

    def __init__(
        self,
        event_bus: EventBus,
        max_hearts: int = 3,
        current_hearts: float = 3.0,
        stone_count: int = 0,
    ) -> None:
        self._event_bus = event_bus
        self._max_hearts = max_hearts
        self._current_hearts = current_hearts
        self._stone_count = stone_count

        # Pre-render a small font for the stone count.
        self._font: pygame.font.Font | None = None
        self._init_font()

        # Subscribe to events.
        self._event_bus.subscribe("heart_collected", self._on_heart_collected)
        self._event_bus.subscribe("stone_collected", self._on_stone_collected)
        self._event_bus.subscribe("damage_taken", self._on_damage_taken)

    def _init_font(self) -> None:
        """Initialize the pixel font for stone count display."""
        try:
            self._font = pygame.font.Font(None, 16)
        except Exception:
            self._font = None

    # ── Public API ────────────────────────────────────────────────

    @property
    def max_hearts(self) -> int:
        """Maximum number of hearts."""
        return self._max_hearts

    @max_hearts.setter
    def max_hearts(self, value: int) -> None:
        self._max_hearts = value

    @property
    def current_hearts(self) -> float:
        """Current health in hearts (supports half-heart granularity)."""
        return self._current_hearts

    @current_hearts.setter
    def current_hearts(self, value: float) -> None:
        self._current_hearts = max(0.0, min(value, float(self._max_hearts)))

    @property
    def stone_count(self) -> int:
        """Current stone count displayed."""
        return self._stone_count

    @stone_count.setter
    def stone_count(self, value: int) -> None:
        self._stone_count = max(0, value)

    def set_state(
        self,
        max_hearts: int | None = None,
        current_hearts: float | None = None,
        stone_count: int | None = None,
    ) -> None:
        """Directly set HUD state (used during initialization or reset).

        Args:
            max_hearts: New max hearts, or None to keep current.
            current_hearts: New current hearts, or None to keep current.
            stone_count: New stone count, or None to keep current.
        """
        if max_hearts is not None:
            self._max_hearts = max_hearts
        if current_hearts is not None:
            self._current_hearts = max(
                0.0, min(current_hearts, float(self._max_hearts))
            )
        if stone_count is not None:
            self._stone_count = max(0, stone_count)

    # ── Rendering ─────────────────────────────────────────────────

    def render(self, surface: pygame.Surface) -> None:
        """Draw the HUD onto the target surface (screen space).

        Args:
            surface: The pygame Surface to draw on (base resolution).
        """
        self._render_hearts(surface)
        self._render_stone_count(surface)

    def _render_hearts(self, surface: pygame.Surface) -> None:
        """Draw heart icons in the top-left corner."""
        x = _HEART_MARGIN_X
        y = _HEART_MARGIN_Y

        for i in range(self._max_hearts):
            heart_x = x + i * (_HEART_SIZE + _HEART_SPACING)

            # Determine fill level for this heart.
            remaining = self._current_hearts - float(i)
            if remaining >= 1.0:
                color = _HEART_FULL_COLOR
            elif remaining >= 0.5:
                color = _HEART_HALF_COLOR
            else:
                color = _HEART_EMPTY_COLOR

            # Draw a diamond shape for each heart.
            cx = heart_x + _HEART_SIZE // 2
            cy = y + _HEART_SIZE // 2
            half = _HEART_SIZE // 2
            points = [
                (cx, y),                    # top
                (heart_x + _HEART_SIZE, cy),# right
                (cx, y + _HEART_SIZE),      # bottom
                (heart_x, cy),              # left
            ]
            pygame.draw.polygon(surface, color, points)

            # Outline for visibility.
            outline_color = tuple(max(0, c - 60) for c in color)
            pygame.draw.polygon(surface, outline_color, points, 1)

    def _render_stone_count(self, surface: pygame.Surface) -> None:
        """Draw stone icon and count in the top-right corner."""
        screen_w = surface.get_width()

        # Stone icon (grey circle).
        icon_x = screen_w - _STONE_MARGIN_X - _STONE_ICON_RADIUS * 2 - 30
        icon_cy = _STONE_MARGIN_Y + _STONE_ICON_RADIUS
        pygame.draw.circle(
            surface,
            _STONE_ICON_COLOR,
            (icon_x + _STONE_ICON_RADIUS, icon_cy),
            _STONE_ICON_RADIUS,
        )
        pygame.draw.circle(
            surface,
            (120, 120, 120),
            (icon_x + _STONE_ICON_RADIUS, icon_cy),
            _STONE_ICON_RADIUS,
            1,
        )

        # Stone count text.
        if self._font is not None:
            text_str = f"x{self._stone_count}"
            # Shadow for readability.
            shadow = self._font.render(text_str, False, _STONE_TEXT_SHADOW)
            text = self._font.render(text_str, False, _STONE_TEXT_COLOR)
            text_x = icon_x + _STONE_TEXT_OFFSET_X
            text_y = _STONE_MARGIN_Y - 1
            surface.blit(shadow, (text_x + 1, text_y + 1))
            surface.blit(text, (text_x, text_y))

    # ── Event handlers ────────────────────────────────────────────

    def _on_heart_collected(self, amount: float = 1.0, **kwargs) -> None:
        """Handle heart_collected events.

        Args:
            amount: Hearts to restore.
        """
        self._current_hearts = min(
            self._current_hearts + amount,
            float(self._max_hearts),
        )

    def _on_stone_collected(self, amount: int = 1, **kwargs) -> None:
        """Handle stone_collected events.

        Args:
            amount: Stones collected.
        """
        self._stone_count += amount

    def _on_damage_taken(self, amount: float = 1.0, **kwargs) -> None:
        """Handle damage_taken events.

        Args:
            amount: Damage in hearts.
        """
        self._current_hearts = max(0.0, self._current_hearts - amount)

    # ── Cleanup ───────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Unsubscribe from EventBus events."""
        self._event_bus.unsubscribe("heart_collected", self._on_heart_collected)
        self._event_bus.unsubscribe("stone_collected", self._on_stone_collected)
        self._event_bus.unsubscribe("damage_taken", self._on_damage_taken)
