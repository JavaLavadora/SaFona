"""Publish/subscribe event system for decoupled inter-system communication."""

from collections import defaultdict
from typing import Callable


class EventBus:
    """Publish/subscribe event system for decoupled communication.

    Systems publish game events without knowing who listens.
    Other systems subscribe to events they care about.

    Example:
        bus = EventBus()
        bus.subscribe("player_hit", lambda damage=0: print(f"Ouch! {damage}"))
        bus.publish("player_hit", damage=10)
    """

    def __init__(self) -> None:
        """Initialize the event bus with an empty subscriber registry."""
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type.

        Args:
            event_type: String identifier for the event (e.g. "player_hit").
            callback: Function to invoke when the event is published.
                Must accept keyword arguments matching the event data.
        """
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Remove a callback registration.

        Args:
            event_type: String identifier for the event.
            callback: The previously registered callback to remove.

        Raises:
            ValueError: If the callback is not registered for this event type.
        """
        self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, **data) -> None:
        """Publish an event, invoking all registered callbacks.

        Args:
            event_type: String identifier for the event.
            **data: Keyword arguments passed to each subscriber callback.
        """
        for callback in self._subscribers[event_type]:
            callback(**data)
