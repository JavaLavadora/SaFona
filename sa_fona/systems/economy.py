"""Economy system: stone currency, drop tables, spending, and death rollback.

ALL economy values are loaded from data/economy.json at initialization.
No economy value is hardcoded.  The project owner can edit economy.json
during playtesting to adjust any balance value without touching Python code.

The EconomySystem subscribes to EventBus events for automatic stone
collection and can provide snapshot/restore for death rollback.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from sa_fona.config.settings import DATA_DIR
from sa_fona.core.event_bus import EventBus


class EconomySystem:
    """Manages sling stone currency: collection, spending, drop tables.

    Args:
        event_bus: Shared event bus for cross-system communication.
        economy_path: Path to the economy.json file.  Defaults to
            the standard data directory location.
    """

    def __init__(
        self,
        event_bus: EventBus,
        economy_path: str | None = None,
    ) -> None:
        self._event_bus = event_bus
        if economy_path is None:
            economy_path = str(DATA_DIR / "economy.json")
        self._economy_path = economy_path

        self._stone_count: int = 0
        self._config: dict[str, Any] = {}
        self._load_config()

        # Subscribe to EventBus events.
        self._event_bus.subscribe("stone_collected", self._on_stone_collected)
        self._event_bus.subscribe("enemy_killed", self._on_enemy_killed)

    # ── Config loading ────────────────────────────────────────────

    def _load_config(self) -> None:
        """Load economy configuration from the JSON file."""
        try:
            with open(self._economy_path, "r", encoding="utf-8") as fh:
                self._config = json.load(fh)
        except FileNotFoundError:
            self._config = {}

    def reload_config(self) -> None:
        """Reload economy.json from disk (hot-reload for playtesting)."""
        self._load_config()

    # ── Stone management ──────────────────────────────────────────

    @property
    def stone_count(self) -> int:
        """Current sling stone count."""
        return self._stone_count

    def add_stones(self, amount: int) -> None:
        """Add stones to the player's wallet.

        Args:
            amount: Number of stones to add (must be >= 0).
        """
        if amount < 0:
            return
        self._stone_count += amount

    def spend_stones(self, amount: int) -> bool:
        """Attempt to spend stones.

        Args:
            amount: Number of stones to spend.

        Returns:
            True if the purchase succeeded, False if insufficient funds.
        """
        if amount < 0 or self._stone_count < amount:
            return False
        self._stone_count -= amount
        return True

    # ── Drop tables ───────────────────────────────────────────────

    def get_enemy_drop(self, enemy_type: str) -> int:
        """Return the stone drop amount for a killed enemy type.

        Args:
            enemy_type: The enemy type key (e.g. "possessed_sheep").

        Returns:
            A random stone amount within the configured range.
        """
        drops = self._config.get("enemy_drops", {})
        entry = drops.get(enemy_type, drops.get("default", {}))
        min_stones = entry.get("stones_min", 1)
        max_stones = entry.get("stones_max", 3)
        return random.randint(min_stones, max_stones)

    def get_enemy_heart_chance(self, enemy_type: str) -> float:
        """Return the heart drop chance for an enemy type.

        Args:
            enemy_type: The enemy type key.

        Returns:
            Probability (0.0 to 1.0) of dropping a heart pickup.
        """
        drops = self._config.get("enemy_drops", {})
        entry = drops.get(enemy_type, drops.get("default", {}))
        return entry.get("heart_chance", 0.1)

    def get_breakable_yield(self, breakable_type: str) -> int:
        """Return the stone yield for a broken object type.

        Args:
            breakable_type: The breakable type key (e.g. "breakable_pot").

        Returns:
            A random stone amount within the configured range.
        """
        drops = self._config.get("stone_drops", {})
        entry = drops.get(breakable_type, {"min": 1, "max": 2})
        return random.randint(entry.get("min", 1), entry.get("max", 2))

    # ── Prices and items ──────────────────────────────────────────

    def get_price(self, item_id: str) -> int:
        """Return the price of a shop item.

        Args:
            item_id: The item identifier.

        Returns:
            The price in stones.
        """
        prices = self._config.get("prices", {})
        return prices.get(item_id, 0)

    def get_heart_upgrade_cost(self, upgrade_index: int) -> int:
        """Return the cost of the Nth heart upgrade (0-indexed).

        Args:
            upgrade_index: The upgrade tier (0 = first upgrade).

        Returns:
            The cost in stones, or 0 if the index is out of range.
        """
        health = self._config.get("health", {})
        costs = health.get("heart_upgrade_costs", [])
        if 0 <= upgrade_index < len(costs):
            return costs[upgrade_index]
        return 0

    def get_consumable_effect(self, item_id: str) -> dict:
        """Return the effect parameters for a consumable item.

        Args:
            item_id: The consumable identifier.

        Returns:
            A dict with effect parameters, or empty dict if not found.
        """
        consumables = self._config.get("consumables", {})
        return consumables.get(item_id, {})

    def get_starting_hearts(self) -> float:
        """Return the starting heart count from config."""
        health = self._config.get("health", {})
        return float(health.get("starting_hearts", 3))

    def get_pickup_value(self, pickup_type: str) -> float:
        """Return the value of a pickup type.

        Args:
            pickup_type: Either "heart" or "stone".

        Returns:
            The value amount for the pickup.
        """
        values = self._config.get("pickup_values", {})
        return float(values.get(pickup_type, 1))

    # ── Config access ─────────────────────────────────────────────

    @property
    def config(self) -> dict[str, Any]:
        """Full economy configuration dict (read-only access)."""
        return self._config

    # ── Snapshot / restore (death rollback) ───────────────────────

    def snapshot(self) -> dict:
        """Return a snapshot of the player's economy state for save/rollback.

        Returns:
            A dict capturing the current stone count.
        """
        return {"stone_count": self._stone_count}

    def restore(self, snapshot: dict) -> None:
        """Restore economy state from a snapshot (death rollback).

        Args:
            snapshot: A dict previously returned by ``snapshot()``.
        """
        self._stone_count = snapshot.get("stone_count", 0)

    # ── Event handlers ────────────────────────────────────────────

    def _on_stone_collected(self, amount: int = 1, **kwargs: Any) -> None:
        """Handle stone_collected events from pickup collection.

        Args:
            amount: Number of stones collected.
        """
        self.add_stones(amount)

    def _on_enemy_killed(self, enemy_type: str = "default", **kwargs: Any) -> None:
        """Handle enemy_killed events to process stone drops.

        Args:
            enemy_type: The type of enemy that was killed.
        """
        stones = self.get_enemy_drop(enemy_type)
        if stones > 0:
            self.add_stones(stones)

    # ── Cleanup ───────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Unsubscribe from EventBus events."""
        self._event_bus.unsubscribe("stone_collected", self._on_stone_collected)
        self._event_bus.unsubscribe("enemy_killed", self._on_enemy_killed)
