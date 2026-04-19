"""Heads-up display: hearts, stone count, and future mask icon.

The HUD renders on top of everything in screen space (not affected by
camera offset).  It subscribes to EventBus events to stay in sync with
game state without directly referencing entity or system objects.

Uses real sprite assets when available (hud_heart.png, hud_stone.png,
mask_stone_slam.png), falling back to simple geometric shapes.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.rendering.asset_loader import load_image, load_ui_asset, load_ui_frame_strip


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

# Mask icon area (below stone count).
_MASK_MARGIN_X: int = 4
_MASK_MARGIN_Y: int = 22
_MASK_ICON_SIZE: int = 14
_MASK_ACTIVE_COLOR: tuple[int, int, int] = (180, 150, 50)
_MASK_EMPTY_COLOR: tuple[int, int, int] = (60, 60, 60)
_MASK_COOLDOWN_COLOR: tuple[int, int, int, int] = (40, 40, 40, 140)


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

        # Mask display state (updated externally each frame).
        self._mask_equipped: bool = False
        self._mask_cooldown_progress: float = 1.0  # 1.0 = ready

        # Pre-render a small font for the stone count.
        self._font: pygame.font.Font | None = None
        self._init_font()

        # Asset sprites (loaded lazily on first render).
        self._heart_frames: list[pygame.Surface] | None = None
        self._stone_icon: pygame.Surface | None = None
        self._mask_icon: pygame.Surface | None = None
        self._assets_loaded: bool = False

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

    def set_mask_state(
        self,
        equipped: bool,
        cooldown_progress: float = 1.0,
    ) -> None:
        """Update the mask display state each frame.

        Args:
            equipped: Whether any mask is currently equipped.
            cooldown_progress: 0.0 (just used) to 1.0 (ready).
        """
        self._mask_equipped = equipped
        self._mask_cooldown_progress = cooldown_progress

    # ── Rendering ─────────────────────────────────────────────────

    def _load_assets(self) -> None:
        """Load HUD sprite assets from disk (called once on first render)."""
        self._assets_loaded = True
        self._heart_frames = load_ui_frame_strip("hud_heart")
        self._stone_icon = load_ui_asset("hud_stone")
        self._mask_icon = load_ui_asset("mask_stone_slam")

    def render(self, surface: pygame.Surface) -> None:
        """Draw the HUD onto the target surface (screen space).

        Args:
            surface: The pygame Surface to draw on (base resolution).
        """
        if not self._assets_loaded:
            self._load_assets()
        self._render_hearts(surface)
        self._render_stone_count(surface)
        self._render_mask_icon(surface)

    def _render_hearts(self, surface: pygame.Surface) -> None:
        """Draw heart icons in the top-left corner.

        Uses hud_heart.png frame strip (full/half/empty) when available,
        falls back to drawn diamond shapes.
        """
        x = _HEART_MARGIN_X
        y = _HEART_MARGIN_Y

        for i in range(self._max_hearts):
            heart_x = x + i * (_HEART_SIZE + _HEART_SPACING)

            # Determine fill level for this heart.
            remaining = self._current_hearts - float(i)
            if remaining >= 1.0:
                frame_idx = 0  # full
                color = _HEART_FULL_COLOR
            elif remaining >= 0.5:
                frame_idx = 1  # half
                color = _HEART_HALF_COLOR
            else:
                frame_idx = 2  # empty
                color = _HEART_EMPTY_COLOR

            # Use sprite frames if available.
            if self._heart_frames and frame_idx < len(self._heart_frames):
                surface.blit(self._heart_frames[frame_idx], (heart_x, y))
                continue

            # Fallback: draw a diamond shape.
            cx = heart_x + _HEART_SIZE // 2
            cy = y + _HEART_SIZE // 2
            points = [
                (cx, y),                    # top
                (heart_x + _HEART_SIZE, cy),# right
                (cx, y + _HEART_SIZE),      # bottom
                (heart_x, cy),              # left
            ]
            pygame.draw.polygon(surface, color, points)
            outline_color = tuple(max(0, c - 60) for c in color)
            pygame.draw.polygon(surface, outline_color, points, 1)

    def _render_stone_count(self, surface: pygame.Surface) -> None:
        """Draw stone icon and count in the top-right corner.

        Uses hud_stone.png when available, falls back to a grey circle.
        """
        screen_w = surface.get_width()

        # Stone icon position.
        icon_x = screen_w - _STONE_MARGIN_X - _STONE_ICON_RADIUS * 2 - 30
        icon_cy = _STONE_MARGIN_Y + _STONE_ICON_RADIUS

        if self._stone_icon is not None:
            # Center the sprite icon at the same position.
            ix = icon_x
            iy = _STONE_MARGIN_Y
            surface.blit(self._stone_icon, (ix, iy))
        else:
            # Fallback: grey circle.
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
            shadow = self._font.render(text_str, False, _STONE_TEXT_SHADOW)
            text = self._font.render(text_str, False, _STONE_TEXT_COLOR)
            text_x = icon_x + _STONE_TEXT_OFFSET_X
            text_y = _STONE_MARGIN_Y - 1
            surface.blit(shadow, (text_x + 1, text_y + 1))
            surface.blit(text, (text_x, text_y))

    def _render_mask_icon(self, surface: pygame.Surface) -> None:
        """Draw the mask icon with cooldown overlay in the top-right corner.

        Uses mask_stone_slam.png when available for the equipped state,
        falling back to colored rectangles.
        """
        screen_w = surface.get_width()
        icon_x = screen_w - _MASK_MARGIN_X - _MASK_ICON_SIZE
        icon_y = _MASK_MARGIN_Y

        if self._mask_equipped:
            if self._mask_icon is not None:
                # Use the real mask sprite (scaled to icon size if needed).
                mask_w = self._mask_icon.get_width()
                mask_h = self._mask_icon.get_height()
                if mask_w != _MASK_ICON_SIZE or mask_h != _MASK_ICON_SIZE:
                    scaled = pygame.transform.scale(
                        self._mask_icon, (_MASK_ICON_SIZE, _MASK_ICON_SIZE),
                    )
                    surface.blit(scaled, (icon_x, icon_y))
                else:
                    surface.blit(self._mask_icon, (icon_x, icon_y))
            else:
                # Fallback: golden square.
                pygame.draw.rect(
                    surface, _MASK_ACTIVE_COLOR,
                    (icon_x, icon_y, _MASK_ICON_SIZE, _MASK_ICON_SIZE),
                )
                pygame.draw.rect(
                    surface, (140, 110, 30),
                    (icon_x, icon_y, _MASK_ICON_SIZE, _MASK_ICON_SIZE), 1,
                )

            # Cooldown overlay: darkened portion shrinks from top.
            if self._mask_cooldown_progress < 1.0:
                cooldown_h = int(
                    _MASK_ICON_SIZE * (1.0 - self._mask_cooldown_progress)
                )
                if cooldown_h > 0:
                    cd_surf = pygame.Surface(
                        (_MASK_ICON_SIZE, cooldown_h), pygame.SRCALPHA,
                    )
                    cd_surf.fill(_MASK_COOLDOWN_COLOR)
                    surface.blit(cd_surf, (icon_x, icon_y))
        else:
            # Empty placeholder (dimmed square).
            pygame.draw.rect(
                surface, _MASK_EMPTY_COLOR,
                (icon_x, icon_y, _MASK_ICON_SIZE, _MASK_ICON_SIZE),
            )
            pygame.draw.rect(
                surface, (40, 40, 40),
                (icon_x, icon_y, _MASK_ICON_SIZE, _MASK_ICON_SIZE), 1,
            )

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
