"""Shop overlay UI rendering.

Draws the shop interface as a semi-transparent overlay on top of
gameplay. Handles two tabs (Items and Masks), item lists with prices,
cursor navigation, and purchase feedback text.

Rendering uses simple text and coloured rectangles consistent with
the project's placeholder aesthetic.
"""

from __future__ import annotations

from typing import Any

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH


# ── Layout constants ──────────────────────────────────────────────
_OVERLAY_COLOR: tuple[int, int, int, int] = (0, 0, 0, 160)
_PANEL_MARGIN_X: int = 30
_PANEL_MARGIN_Y: int = 20
_PANEL_BG: tuple[int, int, int, int] = (20, 18, 30, 230)
_PANEL_BORDER: tuple[int, int, int] = (200, 180, 130)

# Tab header area.
_TAB_HEIGHT: int = 18
_TAB_ACTIVE_COLOR: tuple[int, int, int] = (255, 220, 100)
_TAB_INACTIVE_COLOR: tuple[int, int, int] = (140, 130, 110)

# Item list.
_ITEM_START_Y: int = 24
_ITEM_ROW_HEIGHT: int = 18
_CURSOR_COLOR: tuple[int, int, int] = (255, 220, 100)
_ITEM_NAME_COLOR: tuple[int, int, int] = (255, 255, 255)
_ITEM_PRICE_COLOR: tuple[int, int, int] = (180, 180, 180)
_ITEM_DESC_COLOR: tuple[int, int, int] = (160, 160, 160)
_ITEM_EQUIPPED_COLOR: tuple[int, int, int] = (100, 255, 100)

# Stone count display.
_STONE_DISPLAY_COLOR: tuple[int, int, int] = (200, 200, 200)

# Feedback text.
_FEEDBACK_SUCCESS_COLOR: tuple[int, int, int] = (100, 255, 100)
_FEEDBACK_FAIL_COLOR: tuple[int, int, int] = (255, 80, 80)
_FEEDBACK_DURATION: float = 1.5


class ShopUI:
    """Renders the shop overlay interface.

    Maintains visual state for tabs, cursor position, and feedback
    messages. Actual shop logic (purchases, equip) lives in ShopScene.

    Args:
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
    """

    def __init__(
        self,
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
    ) -> None:
        self._screen_w = screen_width
        self._screen_h = screen_height

        # Font.
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None
        self._init_fonts()

        # Feedback message state.
        self._feedback_text: str = ""
        self._feedback_color: tuple[int, int, int] = _FEEDBACK_SUCCESS_COLOR
        self._feedback_timer: float = 0.0

    def _init_fonts(self) -> None:
        """Initialise pygame fonts for text rendering."""
        try:
            self._font = pygame.font.Font(None, 16)
            self._small_font = pygame.font.Font(None, 14)
        except Exception:
            self._font = None
            self._small_font = None

    # ── Feedback ──────────────────────────────────────────────────

    def show_feedback(self, text: str, success: bool = True) -> None:
        """Display a brief feedback message (e.g. "Purchased!").

        Args:
            text: Message to show.
            success: True for green text, False for red.
        """
        self._feedback_text = text
        self._feedback_color = (
            _FEEDBACK_SUCCESS_COLOR if success else _FEEDBACK_FAIL_COLOR
        )
        self._feedback_timer = _FEEDBACK_DURATION

    def update(self, dt: float) -> None:
        """Tick the feedback timer.

        Args:
            dt: Delta time in seconds.
        """
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._feedback_text = ""

    # ── Rendering ─────────────────────────────────────────────────

    def render(
        self,
        surface: pygame.Surface,
        active_tab: int,
        tab_names: list[str],
        items: list[dict[str, Any]],
        cursor_index: int,
        stone_count: int,
        equipped_mask_id: str | None = None,
    ) -> None:
        """Draw the full shop overlay onto the surface.

        Args:
            surface: The pygame Surface to draw on.
            active_tab: Index of the currently selected tab.
            tab_names: List of tab name strings.
            items: List of item dicts for the current tab.
            cursor_index: Currently highlighted item index.
            stone_count: Player's current stone count.
            equipped_mask_id: ID of the currently equipped mask (for
                the Masks tab display).
        """
        # Semi-transparent dark overlay.
        overlay = pygame.Surface(
            (self._screen_w, self._screen_h), pygame.SRCALPHA,
        )
        overlay.fill(_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        # Panel background.
        px = _PANEL_MARGIN_X
        py = _PANEL_MARGIN_Y
        pw = self._screen_w - _PANEL_MARGIN_X * 2
        ph = self._screen_h - _PANEL_MARGIN_Y * 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill(_PANEL_BG)
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, _PANEL_BORDER, (px, py, pw, ph), 1)

        if self._font is None:
            return

        # Tab headers.
        self._render_tabs(surface, px, py, pw, active_tab, tab_names)

        # Item list.
        list_y = py + _TAB_HEIGHT + 6
        self._render_items(
            surface, px + 8, list_y, pw - 16, items, cursor_index,
            equipped_mask_id,
        )

        # Stone count (bottom-left of panel).
        stone_text = f"Stones: {stone_count}"
        stone_surf = self._font.render(stone_text, False, _STONE_DISPLAY_COLOR)
        surface.blit(stone_surf, (px + 8, py + ph - 18))

        # Close hint (bottom-right of panel).
        hint = self._small_font or self._font
        hint_surf = hint.render("[Esc] Close", False, _TAB_INACTIVE_COLOR)
        surface.blit(
            hint_surf, (px + pw - hint_surf.get_width() - 8, py + ph - 18),
        )

        # Feedback message (centre of panel).
        if self._feedback_text and self._feedback_timer > 0:
            fb_surf = self._font.render(
                self._feedback_text, False, self._feedback_color,
            )
            fb_x = px + (pw - fb_surf.get_width()) // 2
            fb_y = py + ph - 34
            surface.blit(fb_surf, (fb_x, fb_y))

    def _render_tabs(
        self,
        surface: pygame.Surface,
        px: int,
        py: int,
        pw: int,
        active_tab: int,
        tab_names: list[str],
    ) -> None:
        """Draw tab headers at the top of the panel.

        Args:
            surface: Target surface.
            px: Panel X offset.
            py: Panel Y offset.
            pw: Panel width.
            active_tab: Currently active tab index.
            tab_names: List of tab name strings.
        """
        if self._font is None:
            return

        tab_w = pw // max(len(tab_names), 1)
        for i, name in enumerate(tab_names):
            tx = px + i * tab_w
            color = _TAB_ACTIVE_COLOR if i == active_tab else _TAB_INACTIVE_COLOR

            # Underline the active tab.
            if i == active_tab:
                pygame.draw.line(
                    surface, color,
                    (tx + 4, py + _TAB_HEIGHT - 2),
                    (tx + tab_w - 4, py + _TAB_HEIGHT - 2),
                )

            text_surf = self._font.render(name, False, color)
            text_x = tx + (tab_w - text_surf.get_width()) // 2
            surface.blit(text_surf, (text_x, py + 4))

    def _render_items(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        items: list[dict[str, Any]],
        cursor_index: int,
        equipped_mask_id: str | None = None,
    ) -> None:
        """Draw the item list with cursor and details.

        Args:
            surface: Target surface.
            x: Left edge of the list area.
            y: Top edge of the list area.
            width: Available width for text.
            items: List of item dicts to display.
            cursor_index: Index of the highlighted item.
            equipped_mask_id: Currently equipped mask ID for
                displaying equip status.
        """
        if self._font is None:
            return

        if not items:
            empty = self._font.render("(No items available)", False, _ITEM_DESC_COLOR)
            surface.blit(empty, (x, y))
            return

        for i, item in enumerate(items):
            row_y = y + i * _ITEM_ROW_HEIGHT
            is_selected = i == cursor_index

            # Cursor arrow.
            if is_selected:
                arrow = self._font.render(">", False, _CURSOR_COLOR)
                surface.blit(arrow, (x, row_y))

            # Item name.
            name = item.get("name", "???")
            name_color = _ITEM_NAME_COLOR
            name_surf = self._font.render(name, False, name_color)
            surface.blit(name_surf, (x + 12, row_y))

            # Price or equip status.
            price = item.get("price")
            if price is not None:
                price_text = f"{price} stones"
                price_surf = self._font.render(
                    price_text, False, _ITEM_PRICE_COLOR,
                )
                surface.blit(
                    price_surf, (x + width - price_surf.get_width(), row_y),
                )
            else:
                # Mask tab: show equip status.
                mask_id = item.get("id", "")
                if mask_id and mask_id == equipped_mask_id:
                    eq_surf = self._font.render(
                        "[Equipped]", False, _ITEM_EQUIPPED_COLOR,
                    )
                    surface.blit(
                        eq_surf, (x + width - eq_surf.get_width(), row_y),
                    )

            # Description on selected item (below the row).
            if is_selected and self._small_font:
                desc = item.get("description", "")
                if desc:
                    desc_surf = self._small_font.render(
                        desc, False, _ITEM_DESC_COLOR,
                    )
                    surface.blit(desc_surf, (x + 12, row_y + 11))
