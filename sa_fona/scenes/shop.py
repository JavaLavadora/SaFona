"""Shop overlay scene for purchasing items and equipping masks.

Pushes on top of GameplayScene as a transparent overlay.  The player
navigates two tabs (Items and Masks), purchases consumables or upgrades,
and equips/unequips unlocked masks.

The scene reads inventory data from ``data/shop/shop_inventory.json``
and delegates rendering to :class:`~sa_fona.ui.shop_ui.ShopUI`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH, DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.economy import EconomySystem
from sa_fona.systems.mask_system import MaskSystem
from sa_fona.ui.shop_ui import ShopUI


# Tab indices.
_TAB_ITEMS: int = 0
_TAB_MASKS: int = 1
_TAB_NAMES: list[str] = ["Items", "Masks"]


class ShopScene(BaseScene):
    """Overlay scene that presents the shop UI.

    Args:
        event_bus: Shared event bus for publishing purchase events.
        economy: The economy system (stone management).
        mask_system: The mask system (unlock/equip state).
        combat_system: The combat system (for applying heart effects).
        hud: The HUD (for syncing heart/stone display).
        current_world: Current world number for item filtering.
        on_close: Callback invoked when the player closes the shop.
        inventory_path: Path to the shop inventory JSON. Defaults to
            the standard data directory location.
    """

    def __init__(
        self,
        event_bus: EventBus,
        economy: EconomySystem,
        mask_system: MaskSystem,
        combat_system: Any | None = None,
        hud: Any | None = None,
        current_world: int = 1,
        on_close: Callable[[], None] | None = None,
        inventory_path: str | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._economy = economy
        self._mask_system = mask_system
        self._combat = combat_system
        self._hud = hud
        self._current_world = current_world
        self._on_close = on_close
        self._done = False

        # Load shop inventory.
        if inventory_path is None:
            inventory_path = str(DATA_DIR / "shop" / "shop_inventory.json")
        self._inventory = self._load_inventory(inventory_path)

        # Filter items by world availability.
        self._available_items = self._filter_items(
            self._inventory, self._current_world,
        )

        # Track per-item purchase counts for max_purchases enforcement.
        self._purchase_counts: dict[str, int] = {}

        # Navigation state.
        self._active_tab: int = _TAB_ITEMS
        self._cursor_index: int = 0

        # One-shot key tracking for up/down navigation.
        self._prev_up: bool = False
        self._prev_down: bool = False

        # UI renderer.
        self._ui = ShopUI()

    # ── Properties ────────────────────────────────────────────────

    @property
    def is_overlay(self) -> bool:
        """This scene renders on top of gameplay."""
        return True

    @property
    def done(self) -> bool:
        """Whether the shop has been closed."""
        return self._done

    @property
    def active_tab(self) -> int:
        """Currently selected tab index."""
        return self._active_tab

    @property
    def cursor_index(self) -> int:
        """Currently highlighted item index."""
        return self._cursor_index

    @property
    def available_items(self) -> list[dict[str, Any]]:
        """Filtered shop items available for the current world."""
        return self._available_items

    @property
    def purchase_counts(self) -> dict[str, int]:
        """Number of times each item has been purchased."""
        return self._purchase_counts

    @property
    def ui(self) -> ShopUI:
        """The UI renderer (exposed for testing)."""
        return self._ui

    # ── Scene lifecycle ───────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered."""

    def on_exit(self) -> None:
        """Scene exited."""

    def handle_input(self, input_state: InputState) -> None:
        """Process shop navigation and actions.

        Args:
            input_state: Current frame's input snapshot.
        """
        if self._done:
            return

        # Close the shop.
        if input_state.pause_pressed:
            self._close()
            return

        # Tab switching.
        if input_state.move_left:
            self._switch_tab(-1)
        elif input_state.move_right:
            self._switch_tab(1)

        # Cursor navigation (one-shot press detection).
        items = self._get_current_tab_items()
        keys = pygame.key.get_pressed()
        up_now = keys[pygame.K_UP] or keys[pygame.K_w]
        down_now = keys[pygame.K_DOWN] or keys[pygame.K_s]

        if down_now and not self._prev_down:
            self._move_cursor(1, len(items))
        if up_now and not self._prev_up:
            self._move_cursor(-1, len(items))

        self._prev_up = up_now
        self._prev_down = down_now

        # Purchase / equip.
        if input_state.interact_pressed or input_state.jump_pressed:
            if items:
                self._activate_item(items[self._cursor_index])

    def update(self, dt: float) -> None:
        """Update UI timers.

        Args:
            dt: Delta time in seconds.
        """
        self._ui.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Render the shop overlay.

        Args:
            surface: The pygame Surface to draw on.
        """
        items = self._get_current_tab_items()
        self._ui.render(
            surface,
            active_tab=self._active_tab,
            tab_names=_TAB_NAMES,
            items=items,
            cursor_index=self._cursor_index,
            stone_count=self._economy.stone_count,
            equipped_mask_id=self._mask_system.active_mask_id,
        )

    # ── Tab logic ─────────────────────────────────────────────────

    def _switch_tab(self, direction: int) -> None:
        """Switch to another tab.

        Args:
            direction: -1 for left, +1 for right.
        """
        new_tab = self._active_tab + direction
        if 0 <= new_tab < len(_TAB_NAMES):
            self._active_tab = new_tab
            self._cursor_index = 0

    def _move_cursor(self, direction: int, item_count: int) -> None:
        """Move the cursor up or down in the item list.

        Args:
            direction: -1 for up, +1 for down.
            item_count: Number of items in the current list.
        """
        if item_count == 0:
            self._cursor_index = 0
            return
        self._cursor_index = (self._cursor_index + direction) % item_count

    def _get_current_tab_items(self) -> list[dict[str, Any]]:
        """Return the item list for the active tab.

        Returns:
            Items tab: filtered purchasable items.
            Masks tab: unlocked mask entries (with no price).
        """
        if self._active_tab == _TAB_ITEMS:
            return self._get_purchasable_items()
        else:
            return self._get_mask_entries()

    def _get_purchasable_items(self) -> list[dict[str, Any]]:
        """Return items still available for purchase.

        Excludes items that have reached their max_purchases limit.

        Returns:
            Filtered list of item dicts.
        """
        result: list[dict[str, Any]] = []
        for item in self._available_items:
            max_p = item.get("max_purchases", -1)
            bought = self._purchase_counts.get(item["id"], 0)
            if max_p != -1 and bought >= max_p:
                continue
            result.append(item)
        return result

    def _get_mask_entries(self) -> list[dict[str, Any]]:
        """Build a display list from the mask system's unlocked masks.

        Returns:
            List of dicts with id, name, and description for each
            unlocked mask.
        """
        entries: list[dict[str, Any]] = []
        for mask_id in self._mask_system.unlocked_masks:
            mask_def = self._mask_system.definitions.get(mask_id, {})
            entries.append({
                "id": mask_id,
                "name": mask_def.get("name", mask_id),
                "description": mask_def.get("description", ""),
            })
        return entries

    # ── Purchase / equip logic ────────────────────────────────────

    def _activate_item(self, item: dict[str, Any]) -> None:
        """Handle selecting an item (purchase or equip/unequip).

        Args:
            item: The item dict for the selected entry.
        """
        if self._active_tab == _TAB_ITEMS:
            self._purchase_item(item)
        else:
            self._toggle_mask(item)

    def _purchase_item(self, item: dict[str, Any]) -> None:
        """Attempt to purchase a shop item.

        Checks affordability and max_purchases, deducts stones, applies
        the item effect, and publishes a ``shop_purchase`` event.

        Args:
            item: The item dict to purchase.
        """
        item_id = item["id"]
        price = item.get("price", 0)

        # Max-purchases check.
        max_p = item.get("max_purchases", -1)
        bought = self._purchase_counts.get(item_id, 0)
        if max_p != -1 and bought >= max_p:
            self._ui.show_feedback("Already purchased!", success=False)
            return

        # Affordability check.
        if not self._economy.spend_stones(price):
            self._ui.show_feedback("Not enough stones!", success=False)
            return

        # Apply effect.
        effect_type = item.get("effect_type", "")
        effect_value = item.get("effect_value", 0)
        self._apply_effect(effect_type, effect_value)

        # Track purchase.
        self._purchase_counts[item_id] = bought + 1

        # Publish event.
        self._event_bus.publish(
            "shop_purchase", item_id=item_id, price=price,
        )

        self._ui.show_feedback("Purchased!", success=True)

    def _apply_effect(self, effect_type: str, effect_value: Any) -> None:
        """Apply an item's effect to game state.

        Args:
            effect_type: The type of effect (``"heal"`` or ``"heart_upgrade"``).
            effect_value: The magnitude of the effect.
        """
        if effect_type == "heal":
            self._event_bus.publish(
                "heart_collected", amount=float(effect_value),
            )
            # Also update combat system if available.
            if self._combat is not None:
                new_hp = min(
                    self._combat.player_hearts + float(effect_value),
                    float(self._combat.player_max_hearts),
                )
                self._combat.set_player_health(
                    new_hp, self._combat.player_max_hearts,
                )
        elif effect_type == "heart_upgrade":
            value = int(effect_value)
            if self._combat is not None:
                new_max = self._combat.player_max_hearts + value
                new_hp = self._combat.player_hearts + float(value)
                self._combat.set_player_health(new_hp, new_max)
            if self._hud is not None:
                new_max_hud = self._hud.max_hearts + value
                self._hud.set_state(
                    max_hearts=new_max_hud,
                    current_hearts=self._hud.current_hearts + float(value),
                )

    def _toggle_mask(self, item: dict[str, Any]) -> None:
        """Equip or unequip a mask.

        Args:
            item: The mask entry dict (must have an ``"id"`` key).
        """
        mask_id = item.get("id", "")
        if not mask_id:
            return

        if self._mask_system.active_mask_id == mask_id:
            self._mask_system.unequip_mask()
            self._ui.show_feedback("Unequipped!", success=True)
        else:
            if self._mask_system.equip_mask(mask_id):
                self._ui.show_feedback("Equipped!", success=True)
            else:
                self._ui.show_feedback("Cannot equip!", success=False)

    # ── Close ─────────────────────────────────────────────────────

    def _close(self) -> None:
        """Mark the shop as done and invoke the callback."""
        self._done = True
        if self._on_close:
            self._on_close()

    # ── Inventory loading ─────────────────────────────────────────

    @staticmethod
    def _load_inventory(path: str) -> list[dict[str, Any]]:
        """Load shop inventory items from a JSON file.

        Args:
            path: Filesystem path to the inventory JSON.

        Returns:
            List of item dicts, or an empty list on error.
        """
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data.get("items", [])
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    @staticmethod
    def _filter_items(
        items: list[dict[str, Any]], current_world: int,
    ) -> list[dict[str, Any]]:
        """Filter items by the current world's unlock_world threshold.

        Args:
            items: Full inventory list.
            current_world: The world the player is currently in.

        Returns:
            Items whose ``unlock_world`` is <= ``current_world``.
        """
        return [
            item for item in items
            if item.get("unlock_world", 1) <= current_world
        ]
