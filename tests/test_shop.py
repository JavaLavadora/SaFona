"""Tests for the shop system: inventory, purchases, masks, NPC interaction."""

from __future__ import annotations

import json
import os
import tempfile

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.npc import NPC
from sa_fona.scenes.shop import ShopScene
from sa_fona.systems.economy import EconomySystem
from sa_fona.systems.mask_system import MaskSystem


# ── Helpers ──────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialised for every test."""
    pygame.init()
    pygame.display.set_mode((384, 216))
    yield
    pygame.quit()


def _write_json(data: dict | list, suffix: str = ".json") -> str:
    """Write data to a temp JSON file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh)
    return path


def _make_inventory(items: list[dict] | None = None) -> str:
    """Create a temporary shop inventory JSON and return its path."""
    if items is None:
        items = [
            {
                "id": "ensaimada",
                "name": "Ensaimada",
                "description": "Heals 1 heart.",
                "price": 10,
                "effect_type": "heal",
                "effect_value": 1.0,
                "unlock_world": 1,
                "max_purchases": -1,
            },
            {
                "id": "heart_upgrade_1",
                "name": "Heart Container",
                "description": "Max hearts +1.",
                "price": 40,
                "effect_type": "heart_upgrade",
                "effect_value": 1,
                "unlock_world": 1,
                "max_purchases": 1,
            },
            {
                "id": "world2_item",
                "name": "World 2 Only",
                "description": "Only in world 2.",
                "price": 5,
                "effect_type": "heal",
                "effect_value": 0.5,
                "unlock_world": 2,
                "max_purchases": -1,
            },
        ]
    return _write_json({"items": items})


def _make_economy(event_bus: EventBus) -> EconomySystem:
    """Create an EconomySystem with a minimal config."""
    config = {
        "health": {"starting_hearts": 3, "max_hearts_cap": 8},
        "prices": {"ensaimada": 10, "heart_upgrade_1": 40},
    }
    path = _write_json(config)
    return EconomySystem(event_bus, economy_path=path)


def _make_masks(event_bus: EventBus) -> MaskSystem:
    """Create a MaskSystem with one mask definition."""
    defs = {
        "stone_slam": {
            "name": "Stone Slam",
            "description": "Ground pound shockwave.",
            "power_type": "ground_pound",
            "range_tiles": 3,
            "cooldown": 2.0,
        },
    }
    path = _write_json(defs)
    return MaskSystem(event_bus, masks_path=path)


class FakeCombat:
    """Minimal stand-in for CombatSystem, tracking health changes."""

    def __init__(self, hearts: float = 3.0, max_hearts: int = 3):
        self._hearts = hearts
        self._max_hearts = max_hearts

    @property
    def player_hearts(self) -> float:
        return self._hearts

    @property
    def player_max_hearts(self) -> int:
        return self._max_hearts

    def set_player_health(self, current: float, max_hearts: int) -> None:
        self._hearts = current
        self._max_hearts = max_hearts


class FakeHUD:
    """Minimal stand-in for HUD, tracking display state."""

    def __init__(self, max_hearts: int = 3, current_hearts: float = 3.0):
        self._max_hearts = max_hearts
        self._current_hearts = current_hearts

    @property
    def max_hearts(self) -> int:
        return self._max_hearts

    @property
    def current_hearts(self) -> float:
        return self._current_hearts

    def set_state(self, **kwargs) -> None:
        if "max_hearts" in kwargs:
            self._max_hearts = kwargs["max_hearts"]
        if "current_hearts" in kwargs:
            self._current_hearts = kwargs["current_hearts"]


def _make_shop(
    event_bus: EventBus | None = None,
    economy: EconomySystem | None = None,
    mask_system: MaskSystem | None = None,
    combat: FakeCombat | None = None,
    hud: FakeHUD | None = None,
    current_world: int = 1,
    inventory_path: str | None = None,
) -> ShopScene:
    """Create a ShopScene with sensible defaults."""
    if event_bus is None:
        event_bus = EventBus()
    if economy is None:
        economy = _make_economy(event_bus)
    if mask_system is None:
        mask_system = _make_masks(event_bus)
    if combat is None:
        combat = FakeCombat()
    if hud is None:
        hud = FakeHUD()
    if inventory_path is None:
        inventory_path = _make_inventory()
    return ShopScene(
        event_bus=event_bus,
        economy=economy,
        mask_system=mask_system,
        combat_system=combat,
        hud=hud,
        current_world=current_world,
        inventory_path=inventory_path,
    )


# ── Inventory loading ────────────────────────────────────────────


class TestInventoryLoading:
    """Tests for loading and filtering shop inventory."""

    def test_loads_items_from_json(self):
        """Shop loads items from the inventory JSON file."""
        shop = _make_shop()
        # World 1 items only (world2_item filtered out).
        assert len(shop.available_items) == 2
        ids = [item["id"] for item in shop.available_items]
        assert "ensaimada" in ids
        assert "heart_upgrade_1" in ids

    def test_empty_inventory(self):
        """Shop handles a missing inventory file gracefully."""
        shop = _make_shop(inventory_path="/nonexistent/path.json")
        assert shop.available_items == []

    def test_proto_shop_filtering_world1(self):
        """Only world-1 items are available when current_world is 1."""
        shop = _make_shop(current_world=1)
        for item in shop.available_items:
            assert item.get("unlock_world", 1) <= 1

    def test_world2_items_appear_in_world2(self):
        """World-2 items become available when current_world is 2."""
        shop = _make_shop(current_world=2)
        ids = [item["id"] for item in shop.available_items]
        assert "world2_item" in ids


# ── Purchase flow ────────────────────────────────────────────────


class TestPurchaseFlow:
    """Tests for the item purchase flow."""

    def test_purchase_deducts_stones(self):
        """Buying an ensaimada deducts stones from the economy."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(50)
        shop = _make_shop(event_bus=bus, economy=economy)

        # Simulate selecting the ensaimada (first item).
        items = shop._get_purchasable_items()
        ensaimada = next(i for i in items if i["id"] == "ensaimada")
        shop._purchase_item(ensaimada)

        assert economy.stone_count == 40  # 50 - 10

    def test_purchase_applies_heal(self):
        """Buying an ensaimada heals the player."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(20)
        combat = FakeCombat(hearts=2.0, max_hearts=3)
        shop = _make_shop(event_bus=bus, economy=economy, combat=combat)

        items = shop._get_purchasable_items()
        ensaimada = next(i for i in items if i["id"] == "ensaimada")
        shop._purchase_item(ensaimada)

        assert combat.player_hearts == 3.0  # 2.0 + 1.0

    def test_insufficient_stones_rejected(self):
        """Purchase fails when player lacks enough stones."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(5)  # Not enough for ensaimada (10).
        shop = _make_shop(event_bus=bus, economy=economy)

        items = shop._get_purchasable_items()
        ensaimada = next(i for i in items if i["id"] == "ensaimada")
        shop._purchase_item(ensaimada)

        assert economy.stone_count == 5  # Unchanged.

    def test_purchase_publishes_event(self):
        """A successful purchase publishes a shop_purchase event."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(20)

        events_received: list[dict] = []
        bus.subscribe(
            "shop_purchase",
            lambda **kw: events_received.append(kw),
        )

        shop = _make_shop(event_bus=bus, economy=economy)
        items = shop._get_purchasable_items()
        ensaimada = next(i for i in items if i["id"] == "ensaimada")
        shop._purchase_item(ensaimada)

        assert len(events_received) == 1
        assert events_received[0]["item_id"] == "ensaimada"
        assert events_received[0]["price"] == 10


# ── Heart upgrade ────────────────────────────────────────────────


class TestHeartUpgrade:
    """Tests for heart upgrade purchases."""

    def test_heart_upgrade_increases_max(self):
        """Buying a Heart Container increases max hearts."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(50)
        combat = FakeCombat(hearts=3.0, max_hearts=3)
        hud = FakeHUD(max_hearts=3, current_hearts=3.0)
        shop = _make_shop(
            event_bus=bus, economy=economy, combat=combat, hud=hud,
        )

        items = shop._get_purchasable_items()
        upgrade = next(i for i in items if i["id"] == "heart_upgrade_1")
        shop._purchase_item(upgrade)

        assert combat.player_max_hearts == 4
        assert combat.player_hearts == 4.0
        assert hud.max_hearts == 4
        assert economy.stone_count == 10  # 50 - 40


# ── Max purchases limit ─────────────────────────────────────────


class TestMaxPurchases:
    """Tests for max_purchases limit enforcement."""

    def test_max_purchases_enforced(self):
        """Heart Container can only be bought once (max_purchases=1)."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(100)
        combat = FakeCombat(hearts=3.0, max_hearts=3)
        hud = FakeHUD()
        shop = _make_shop(
            event_bus=bus, economy=economy, combat=combat, hud=hud,
        )

        # First purchase: succeeds.
        items = shop._get_purchasable_items()
        upgrade = next(i for i in items if i["id"] == "heart_upgrade_1")
        shop._purchase_item(upgrade)
        assert shop.purchase_counts["heart_upgrade_1"] == 1

        # Second purchase: rejected (already at max).
        shop._purchase_item(upgrade)
        assert shop.purchase_counts["heart_upgrade_1"] == 1
        assert economy.stone_count == 60  # Only deducted once.

    def test_unlimited_purchases(self):
        """Ensaimada can be bought unlimited times (max_purchases=-1)."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(30)
        shop = _make_shop(event_bus=bus, economy=economy)

        items = shop._get_purchasable_items()
        ensaimada = next(i for i in items if i["id"] == "ensaimada")

        shop._purchase_item(ensaimada)
        shop._purchase_item(ensaimada)
        shop._purchase_item(ensaimada)

        assert shop.purchase_counts["ensaimada"] == 3
        assert economy.stone_count == 0  # 30 - 3*10

    def test_sold_out_item_removed_from_list(self):
        """Items at max_purchases are excluded from the purchasable list."""
        bus = EventBus()
        economy = _make_economy(bus)
        economy.add_stones(100)
        combat = FakeCombat()
        hud = FakeHUD()
        shop = _make_shop(
            event_bus=bus, economy=economy, combat=combat, hud=hud,
        )

        # Buy the heart upgrade (max_purchases=1).
        items = shop._get_purchasable_items()
        upgrade = next(i for i in items if i["id"] == "heart_upgrade_1")
        shop._purchase_item(upgrade)

        # Now the purchasable list should exclude it.
        remaining = shop._get_purchasable_items()
        ids = [i["id"] for i in remaining]
        assert "heart_upgrade_1" not in ids
        assert "ensaimada" in ids


# ── Mask equip / unequip ─────────────────────────────────────────


class TestMaskEquip:
    """Tests for mask equip/unequip from the shop Masks tab."""

    def test_equip_mask(self):
        """Equipping an unlocked mask sets it as active."""
        bus = EventBus()
        mask_system = _make_masks(bus)
        mask_system.unlock_mask("stone_slam")
        # Ensure it starts unequipped.
        mask_system.unequip_mask()

        shop = _make_shop(event_bus=bus, mask_system=mask_system)
        shop._active_tab = 1  # Masks tab.

        mask_entries = shop._get_mask_entries()
        assert len(mask_entries) == 1
        shop._toggle_mask(mask_entries[0])

        assert mask_system.active_mask_id == "stone_slam"

    def test_unequip_mask(self):
        """Toggling an already-equipped mask unequips it."""
        bus = EventBus()
        mask_system = _make_masks(bus)
        mask_system.unlock_mask("stone_slam")
        mask_system.equip_mask("stone_slam")

        shop = _make_shop(event_bus=bus, mask_system=mask_system)
        shop._active_tab = 1

        mask_entries = shop._get_mask_entries()
        shop._toggle_mask(mask_entries[0])

        assert mask_system.active_mask_id is None

    def test_no_masks_unlocked(self):
        """Masks tab shows empty list when no masks are unlocked."""
        bus = EventBus()
        mask_system = _make_masks(bus)  # Nothing unlocked.
        shop = _make_shop(event_bus=bus, mask_system=mask_system)
        shop._active_tab = 1

        assert shop._get_mask_entries() == []


# ── NPC interaction ──────────────────────────────────────────────


class TestNPCInteraction:
    """Tests for the NPC entity and interaction detection."""

    def test_npc_creation(self):
        """NPC entity initialises with correct properties."""
        npc = NPC(100, 200, npc_id="llorencc", npc_type="shop", label="L")
        assert npc.npc_id == "llorencc"
        assert npc.npc_type == "shop"
        assert npc.rect.x == 100
        assert npc.rect.y == 200

    def test_can_interact_when_overlapping(self):
        """Player can interact when overlapping the NPC's interaction zone."""
        npc = NPC(100, 100)
        player_rect = pygame.Rect(90, 100, 24, 32)
        assert npc.can_interact(player_rect) is True

    def test_cannot_interact_when_far(self):
        """Player cannot interact when far from the NPC."""
        npc = NPC(100, 100)
        player_rect = pygame.Rect(300, 300, 24, 32)
        assert npc.can_interact(player_rect) is False

    def test_npc_update_is_noop(self):
        """NPC update does not crash (static entities)."""
        npc = NPC(100, 100)
        npc.update(0.016)  # Should not raise.


# ── Shop scene navigation ───────────────────────────────────────


class TestShopNavigation:
    """Tests for shop tab switching and cursor movement."""

    def test_overlay_property(self):
        """Shop scene is an overlay."""
        shop = _make_shop()
        assert shop.is_overlay is True

    def test_tab_switch(self):
        """Switching tabs changes the active tab and resets cursor."""
        shop = _make_shop()
        assert shop.active_tab == 0
        shop._switch_tab(1)
        assert shop.active_tab == 1
        shop._switch_tab(-1)
        assert shop.active_tab == 0

    def test_tab_clamp(self):
        """Tab switching does not go below 0 or above max."""
        shop = _make_shop()
        shop._switch_tab(-1)
        assert shop.active_tab == 0  # Clamped at 0.
        shop._switch_tab(1)
        shop._switch_tab(1)
        assert shop.active_tab == 1  # Clamped at 1.

    def test_cursor_wraps(self):
        """Cursor wraps around in the item list."""
        shop = _make_shop()
        shop._move_cursor(-1, 2)
        assert shop.cursor_index == 1  # Wrapped to last.
        shop._move_cursor(1, 2)
        assert shop.cursor_index == 0  # Wrapped to first.

    def test_close_sets_done(self):
        """Closing the shop sets done to True."""
        shop = _make_shop()
        assert shop.done is False
        shop._close()
        assert shop.done is True

    def test_close_callback_invoked(self):
        """Closing the shop invokes the on_close callback."""
        called = []
        bus = EventBus()
        shop = ShopScene(
            event_bus=bus,
            economy=_make_economy(bus),
            mask_system=_make_masks(bus),
            on_close=lambda: called.append(True),
            inventory_path=_make_inventory(),
        )
        shop._close()
        assert called == [True]

    def test_escape_closes_shop(self):
        """Pressing Escape closes the shop."""
        shop = _make_shop()
        state = InputState(pause_pressed=True)
        shop.handle_input(state)
        assert shop.done is True


# ── Rendering smoke test ─────────────────────────────────────────


class TestShopRendering:
    """Smoke tests for shop rendering (no visual assertions)."""

    def test_render_items_tab(self):
        """Rendering the Items tab does not crash."""
        shop = _make_shop()
        surface = pygame.Surface((384, 216))
        shop.render(surface)

    def test_render_masks_tab(self):
        """Rendering the Masks tab does not crash."""
        bus = EventBus()
        mask_system = _make_masks(bus)
        mask_system.unlock_mask("stone_slam")
        shop = _make_shop(event_bus=bus, mask_system=mask_system)
        shop._active_tab = 1
        surface = pygame.Surface((384, 216))
        shop.render(surface)

    def test_render_with_feedback(self):
        """Rendering with active feedback text does not crash."""
        shop = _make_shop()
        shop.ui.show_feedback("Purchased!", success=True)
        surface = pygame.Surface((384, 216))
        shop.render(surface)

    def test_feedback_timer_expires(self):
        """Feedback text clears after the timer expires."""
        shop = _make_shop()
        shop.ui.show_feedback("Test", success=True)
        shop.update(2.0)  # Exceed the feedback duration.
        assert shop.ui._feedback_text == ""
