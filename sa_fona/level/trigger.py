"""Level trigger system: rectangular zones that fire events on player entry.

Trigger types include dialogue (starts a dialogue sequence), level_end
(completes the level), and save_point (marks save/shop location).
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.core.event_bus import EventBus


class TriggerType(Enum):
    """Supported trigger types."""

    DIALOGUE = auto()
    LEVEL_END = auto()
    SAVE_POINT = auto()


_TYPE_MAP: dict[str, TriggerType] = {
    "dialogue": TriggerType.DIALOGUE,
    "level_end": TriggerType.LEVEL_END,
    "save_point": TriggerType.SAVE_POINT,
}


class Trigger:
    """A rectangular zone in a level that fires an event when the player enters.

    Attributes:
        rect: Bounding box in world pixels.
        trigger_type: The kind of trigger (dialogue, level_end, save_point).
        once: If True, the trigger fires only once and then deactivates.
        active: Whether the trigger can still fire.
        properties: Extra data (e.g. dialogue_id, shop_available).
    """

    def __init__(
        self,
        rect: pygame.Rect,
        trigger_type: TriggerType,
        once: bool = True,
        properties: dict | None = None,
    ) -> None:
        """Initialize a trigger.

        Args:
            rect: Bounding box in world pixels.
            trigger_type: The kind of trigger.
            once: Whether the trigger fires only once.
            properties: Extra trigger-specific data.
        """
        self.rect = rect
        self.trigger_type = trigger_type
        self.once = once
        self.active = True
        self.properties = properties or {}

    def check(self, player_rect: pygame.Rect) -> bool:
        """Check if the player overlaps this trigger.

        Args:
            player_rect: The player's bounding box in world pixels.

        Returns:
            True if the trigger is active and the player overlaps it.
        """
        if not self.active:
            return False
        return self.rect.colliderect(player_rect)

    def fire(self, event_bus: EventBus) -> None:
        """Publish the trigger event on the event bus.

        If the trigger is ``once``, it deactivates after firing.

        Args:
            event_bus: The event bus to publish the event on.
        """
        if not self.active:
            return

        event_name = f"trigger_{self.trigger_type.name.lower()}"
        event_bus.publish(event_name, trigger=self)

        if self.once:
            self.active = False

    @staticmethod
    def from_dict(data: dict, tile_size: int = 16) -> Trigger:
        """Create a Trigger from a level JSON trigger dict.

        Args:
            data: A trigger definition dict from the level JSON.
                Expected keys: ``type``, ``rect`` (with x, y, w, h in tile
                coords), and optional ``once``, ``dialogue_id``, etc.
            tile_size: Tile size in pixels for coordinate conversion.

        Returns:
            A configured Trigger instance.

        Raises:
            ValueError: If the trigger type is not recognized.
        """
        type_str = data.get("type", "")
        trigger_type = _TYPE_MAP.get(type_str)
        if trigger_type is None:
            raise ValueError(f"Unknown trigger type: {type_str!r}")

        rect_data = data.get("rect", {})
        px_rect = pygame.Rect(
            int(rect_data.get("x", 0)) * tile_size,
            int(rect_data.get("y", 0)) * tile_size,
            int(rect_data.get("w", 1)) * tile_size,
            int(rect_data.get("h", 1)) * tile_size,
        )

        once = data.get("once", True)

        # Collect all extra properties beyond the standard keys.
        standard_keys = {"type", "rect", "once"}
        properties = {k: v for k, v in data.items() if k not in standard_keys}

        return Trigger(
            rect=px_rect,
            trigger_type=trigger_type,
            once=once,
            properties=properties,
        )


class TriggerSystem:
    """Manages all triggers in a level and checks player overlap each frame.

    Args:
        event_bus: Shared event bus for publishing trigger events.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the trigger system.

        Args:
            event_bus: Event bus for broadcasting trigger events.
        """
        self._event_bus = event_bus
        self._triggers: list[Trigger] = []

    @property
    def triggers(self) -> list[Trigger]:
        """The list of managed triggers."""
        return self._triggers

    def add(self, trigger: Trigger) -> None:
        """Register a trigger.

        Args:
            trigger: The trigger to add.
        """
        self._triggers.append(trigger)

    def load_from_list(self, trigger_dicts: list[dict], tile_size: int = 16) -> None:
        """Load triggers from a list of JSON dicts.

        Args:
            trigger_dicts: Raw trigger definitions from the level JSON.
            tile_size: Tile size in pixels.
        """
        for data in trigger_dicts:
            try:
                trigger = Trigger.from_dict(data, tile_size)
                self._triggers.append(trigger)
            except ValueError:
                # Skip unrecognized trigger types gracefully.
                pass

    def update(self, player_rect: pygame.Rect) -> None:
        """Check all active triggers against the player rect.

        Fires events for any triggers the player is overlapping.

        Args:
            player_rect: The player's bounding box in world pixels.
        """
        for trigger in self._triggers:
            if trigger.check(player_rect):
                trigger.fire(self._event_bus)

    def reset(self) -> None:
        """Clear all triggers."""
        self._triggers.clear()
