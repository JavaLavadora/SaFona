"""Tests for the EconomySystem."""

import json
import os
import tempfile

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.systems.economy import EconomySystem


@pytest.fixture
def economy_file(tmp_path):
    """Create a temporary economy.json for testing."""
    data = {
        "version": "1.0",
        "sling": {},
        "health": {
            "starting_hearts": 3,
            "max_hearts_cap": 8,
            "heart_upgrade_costs": [40, 75, 120],
            "half_heart_value": 0.5,
        },
        "consumables": {
            "ensaimada": {
                "display_name": "Ensaimada",
                "effect": "heal",
                "heal_amount": 2.0,
                "price": 10,
                "unlock_world": 1,
            }
        },
        "stone_drops": {
            "breakable_pot": {"min": 1, "max": 3},
            "breakable_crate": {"min": 2, "max": 4},
        },
        "enemy_drops": {
            "default": {"stones_min": 1, "stones_max": 3, "heart_chance": 0.1},
            "possessed_sheep": {"stones_min": 2, "stones_max": 5, "heart_chance": 0.2},
        },
        "prices": {
            "ensaimada": 10,
            "heart_upgrade_1": 40,
        },
        "pickup_values": {
            "heart": 1.0,
            "stone": 1,
        },
    }
    path = tmp_path / "economy.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture
def bus():
    """Create a fresh EventBus."""
    return EventBus()


@pytest.fixture
def economy(bus, economy_file):
    """Create an EconomySystem with test config."""
    return EconomySystem(bus, economy_path=economy_file)


class TestStoneManagement:
    """Tests for stone add/spend operations."""

    def test_initial_stone_count_is_zero(self, economy):
        assert economy.stone_count == 0

    def test_add_stones(self, economy):
        economy.add_stones(10)
        assert economy.stone_count == 10

    def test_add_stones_accumulates(self, economy):
        economy.add_stones(5)
        economy.add_stones(3)
        assert economy.stone_count == 8

    def test_add_negative_stones_is_ignored(self, economy):
        economy.add_stones(5)
        economy.add_stones(-3)
        assert economy.stone_count == 5

    def test_spend_stones_success(self, economy):
        economy.add_stones(10)
        result = economy.spend_stones(7)
        assert result is True
        assert economy.stone_count == 3

    def test_spend_stones_insufficient(self, economy):
        economy.add_stones(5)
        result = economy.spend_stones(10)
        assert result is False
        assert economy.stone_count == 5

    def test_spend_stones_exact(self, economy):
        economy.add_stones(5)
        result = economy.spend_stones(5)
        assert result is True
        assert economy.stone_count == 0

    def test_spend_negative_returns_false(self, economy):
        economy.add_stones(10)
        result = economy.spend_stones(-1)
        assert result is False


class TestSnapshotRestore:
    """Tests for death rollback via snapshot/restore."""

    def test_snapshot_captures_stone_count(self, economy):
        economy.add_stones(42)
        snap = economy.snapshot()
        assert snap["stone_count"] == 42

    def test_restore_resets_stone_count(self, economy):
        economy.add_stones(100)
        snap = economy.snapshot()
        economy.add_stones(50)
        assert economy.stone_count == 150
        economy.restore(snap)
        assert economy.stone_count == 100

    def test_restore_empty_snapshot(self, economy):
        economy.add_stones(10)
        economy.restore({})
        assert economy.stone_count == 0

    def test_snapshot_restore_roundtrip(self, economy):
        economy.add_stones(25)
        snap = economy.snapshot()
        economy.spend_stones(10)
        economy.add_stones(5)
        assert economy.stone_count == 20
        economy.restore(snap)
        assert economy.stone_count == 25


class TestDropTables:
    """Tests for enemy and breakable drop values."""

    def test_enemy_drop_in_range(self, economy):
        for _ in range(20):
            drop = economy.get_enemy_drop("possessed_sheep")
            assert 2 <= drop <= 5

    def test_default_enemy_drop_in_range(self, economy):
        for _ in range(20):
            drop = economy.get_enemy_drop("unknown_type")
            assert 1 <= drop <= 3

    def test_breakable_yield_in_range(self, economy):
        for _ in range(20):
            yield_val = economy.get_breakable_yield("breakable_pot")
            assert 1 <= yield_val <= 3

    def test_breakable_crate_yield_in_range(self, economy):
        for _ in range(20):
            yield_val = economy.get_breakable_yield("breakable_crate")
            assert 2 <= yield_val <= 4

    def test_unknown_breakable_uses_default(self, economy):
        yield_val = economy.get_breakable_yield("unknown_thing")
        assert yield_val >= 1


class TestPricesAndConfig:
    """Tests for price lookups and config access."""

    def test_get_price(self, economy):
        assert economy.get_price("ensaimada") == 10

    def test_get_price_unknown(self, economy):
        assert economy.get_price("nonexistent") == 0

    def test_get_heart_upgrade_cost(self, economy):
        assert economy.get_heart_upgrade_cost(0) == 40
        assert economy.get_heart_upgrade_cost(1) == 75
        assert economy.get_heart_upgrade_cost(2) == 120

    def test_get_heart_upgrade_cost_out_of_range(self, economy):
        assert economy.get_heart_upgrade_cost(99) == 0

    def test_get_consumable_effect(self, economy):
        effect = economy.get_consumable_effect("ensaimada")
        assert effect["effect"] == "heal"
        assert effect["heal_amount"] == 2.0

    def test_get_consumable_effect_unknown(self, economy):
        effect = economy.get_consumable_effect("nonexistent")
        assert effect == {}

    def test_get_starting_hearts(self, economy):
        assert economy.get_starting_hearts() == 3.0

    def test_get_pickup_value(self, economy):
        assert economy.get_pickup_value("heart") == 1.0
        assert economy.get_pickup_value("stone") == 1.0


class TestEventBusIntegration:
    """Tests for EventBus subscription handling."""

    def test_stone_collected_event(self, bus, economy):
        bus.publish("stone_collected", amount=5)
        assert economy.stone_count == 5

    def test_stone_collected_multiple(self, bus, economy):
        bus.publish("stone_collected", amount=3)
        bus.publish("stone_collected", amount=2)
        assert economy.stone_count == 5

    def test_enemy_killed_adds_stones(self, bus, economy):
        bus.publish("enemy_killed", enemy_type="possessed_sheep")
        assert economy.stone_count >= 2

    def test_cleanup_unsubscribes(self, bus, economy):
        economy.cleanup()
        bus.publish("stone_collected", amount=100)
        assert economy.stone_count == 0


class TestReloadConfig:
    """Tests for hot-reload functionality."""

    def test_reload_config(self, bus, economy_file):
        economy = EconomySystem(bus, economy_path=economy_file)
        assert economy.get_price("ensaimada") == 10

        # Update the file.
        with open(economy_file, "r") as f:
            data = json.load(f)
        data["prices"]["ensaimada"] = 20
        with open(economy_file, "w") as f:
            json.dump(data, f)

        economy.reload_config()
        assert economy.get_price("ensaimada") == 20


class TestMissingFile:
    """Tests for missing economy.json graceful fallback."""

    def test_missing_file_does_not_crash(self, bus):
        economy = EconomySystem(bus, economy_path="/nonexistent/path.json")
        assert economy.stone_count == 0
        assert economy.config == {}
