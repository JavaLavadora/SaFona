"""Tests for the level trigger system."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.level.trigger import Trigger, TriggerSystem, TriggerType


class TestTriggerCreation:
    """Tests for Trigger construction and from_dict parsing."""

    def test_trigger_init_defaults(self):
        rect = pygame.Rect(0, 0, 32, 32)
        trigger = Trigger(rect, TriggerType.DIALOGUE)
        assert trigger.trigger_type == TriggerType.DIALOGUE
        assert trigger.once is True
        assert trigger.active is True
        assert trigger.properties == {}

    def test_trigger_init_custom(self):
        rect = pygame.Rect(10, 20, 48, 48)
        props = {"dialogue_id": "test_d"}
        trigger = Trigger(rect, TriggerType.DIALOGUE, once=False, properties=props)
        assert trigger.once is False
        assert trigger.properties["dialogue_id"] == "test_d"

    def test_from_dict_dialogue(self):
        data = {
            "type": "dialogue",
            "rect": {"x": 5, "y": 10, "w": 3, "h": 2},
            "dialogue_id": "hello",
            "once": True,
        }
        trigger = Trigger.from_dict(data, tile_size=16)
        assert trigger.trigger_type == TriggerType.DIALOGUE
        assert trigger.rect == pygame.Rect(80, 160, 48, 32)
        assert trigger.properties["dialogue_id"] == "hello"
        assert trigger.once is True

    def test_from_dict_level_end(self):
        data = {
            "type": "level_end",
            "rect": {"x": 0, "y": 0, "w": 1, "h": 1},
        }
        trigger = Trigger.from_dict(data, tile_size=16)
        assert trigger.trigger_type == TriggerType.LEVEL_END

    def test_from_dict_save_point(self):
        data = {
            "type": "save_point",
            "rect": {"x": 2, "y": 3, "w": 2, "h": 3},
            "shop_available": False,
            "once": False,
        }
        trigger = Trigger.from_dict(data, tile_size=16)
        assert trigger.trigger_type == TriggerType.SAVE_POINT
        assert trigger.once is False
        assert trigger.properties["shop_available"] is False

    def test_from_dict_unknown_type_raises(self):
        data = {"type": "unknown", "rect": {"x": 0, "y": 0, "w": 1, "h": 1}}
        with pytest.raises(ValueError, match="Unknown trigger type"):
            Trigger.from_dict(data)


class TestTriggerCheck:
    """Tests for trigger collision detection."""

    def test_check_overlap_returns_true(self):
        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE)
        player = pygame.Rect(60, 60, 24, 32)
        assert trigger.check(player) is True

    def test_check_no_overlap_returns_false(self):
        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE)
        player = pygame.Rect(200, 200, 24, 32)
        assert trigger.check(player) is False

    def test_check_inactive_returns_false(self):
        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE)
        trigger.active = False
        player = pygame.Rect(60, 60, 24, 32)
        assert trigger.check(player) is False

    def test_check_edge_touching(self):
        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE)
        # Adjacent but not overlapping.
        player = pygame.Rect(82, 50, 24, 32)
        assert trigger.check(player) is False


class TestTriggerFire:
    """Tests for trigger event firing."""

    def test_fire_publishes_event(self):
        bus = EventBus()
        fired = []
        bus.subscribe("trigger_dialogue", lambda trigger=None: fired.append(trigger))

        trigger = Trigger(
            pygame.Rect(0, 0, 32, 32),
            TriggerType.DIALOGUE,
            properties={"dialogue_id": "test"},
        )
        trigger.fire(bus)
        assert len(fired) == 1
        assert fired[0] is trigger

    def test_fire_once_deactivates(self):
        bus = EventBus()
        count = []
        bus.subscribe("trigger_dialogue", lambda trigger=None: count.append(1))

        trigger = Trigger(pygame.Rect(0, 0, 32, 32), TriggerType.DIALOGUE, once=True)
        trigger.fire(bus)
        assert trigger.active is False
        trigger.fire(bus)  # Should not fire again.
        assert len(count) == 1

    def test_fire_repeatable(self):
        bus = EventBus()
        count = []
        bus.subscribe("trigger_save_point", lambda trigger=None: count.append(1))

        trigger = Trigger(
            pygame.Rect(0, 0, 32, 32), TriggerType.SAVE_POINT, once=False
        )
        trigger.fire(bus)
        trigger.fire(bus)
        assert len(count) == 2

    def test_fire_level_end_event_name(self):
        bus = EventBus()
        fired = []
        bus.subscribe("trigger_level_end", lambda trigger=None: fired.append(1))

        trigger = Trigger(pygame.Rect(0, 0, 32, 32), TriggerType.LEVEL_END)
        trigger.fire(bus)
        assert len(fired) == 1


class TestTriggerSystem:
    """Tests for the TriggerSystem manager."""

    def test_add_trigger(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        trigger = Trigger(pygame.Rect(0, 0, 32, 32), TriggerType.DIALOGUE)
        system.add(trigger)
        assert len(system.triggers) == 1

    def test_load_from_list(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        data = [
            {"type": "dialogue", "rect": {"x": 0, "y": 0, "w": 2, "h": 2}, "dialogue_id": "d1"},
            {"type": "level_end", "rect": {"x": 10, "y": 0, "w": 1, "h": 1}},
        ]
        system.load_from_list(data, tile_size=16)
        assert len(system.triggers) == 2

    def test_load_from_list_skips_unknown(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        data = [
            {"type": "dialogue", "rect": {"x": 0, "y": 0, "w": 1, "h": 1}},
            {"type": "boss_gate", "rect": {"x": 5, "y": 0, "w": 1, "h": 1}},
        ]
        system.load_from_list(data, tile_size=16)
        assert len(system.triggers) == 1  # boss_gate not recognized yet

    def test_update_fires_on_overlap(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        fired = []
        bus.subscribe("trigger_dialogue", lambda trigger=None: fired.append(trigger))

        trigger = Trigger(
            pygame.Rect(50, 50, 32, 32),
            TriggerType.DIALOGUE,
            properties={"dialogue_id": "intro"},
        )
        system.add(trigger)

        player = pygame.Rect(60, 60, 24, 32)
        system.update(player)
        assert len(fired) == 1

    def test_update_no_fire_without_overlap(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        fired = []
        bus.subscribe("trigger_dialogue", lambda trigger=None: fired.append(1))

        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE)
        system.add(trigger)

        player = pygame.Rect(200, 200, 24, 32)
        system.update(player)
        assert len(fired) == 0

    def test_update_once_trigger_fires_only_once(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        fired = []
        bus.subscribe("trigger_dialogue", lambda trigger=None: fired.append(1))

        trigger = Trigger(pygame.Rect(50, 50, 32, 32), TriggerType.DIALOGUE, once=True)
        system.add(trigger)

        player = pygame.Rect(60, 60, 24, 32)
        system.update(player)
        system.update(player)  # Second update, trigger should be inactive.
        assert len(fired) == 1

    def test_reset_clears_triggers(self):
        bus = EventBus()
        system = TriggerSystem(bus)
        system.add(Trigger(pygame.Rect(0, 0, 32, 32), TriggerType.DIALOGUE))
        system.reset()
        assert len(system.triggers) == 0
