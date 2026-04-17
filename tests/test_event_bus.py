"""Tests for the EventBus publish/subscribe system."""

from sa_fona.core.event_bus import EventBus


class TestEventBusSubscribeAndPublish:
    """Tests for basic subscribe and publish behavior."""

    def test_subscribe_and_publish_invokes_callback(self) -> None:
        """A subscribed callback should be invoked on publish."""
        bus = EventBus()
        received = []
        bus.subscribe("test_event", lambda: received.append(True))

        bus.publish("test_event")

        assert received == [True]

    def test_publish_with_no_subscribers_does_not_crash(self) -> None:
        """Publishing an event with no subscribers should not raise."""
        bus = EventBus()
        bus.publish("unregistered_event")

    def test_unsubscribe_removes_callback(self) -> None:
        """After unsubscribing, the callback should not be invoked."""
        bus = EventBus()
        received = []
        callback = lambda: received.append(True)
        bus.subscribe("test_event", callback)
        bus.unsubscribe("test_event", callback)

        bus.publish("test_event")

        assert received == []

    def test_multiple_subscribers_all_receive_event(self) -> None:
        """All subscribed callbacks should be invoked on publish."""
        bus = EventBus()
        results = []
        bus.subscribe("multi", lambda: results.append("a"))
        bus.subscribe("multi", lambda: results.append("b"))
        bus.subscribe("multi", lambda: results.append("c"))

        bus.publish("multi")

        assert results == ["a", "b", "c"]

    def test_publish_passes_data_kwargs_to_callback(self) -> None:
        """Published keyword data should be passed to each callback."""
        bus = EventBus()
        received = {}

        def handler(damage: int = 0, source: str = "") -> None:
            received["damage"] = damage
            received["source"] = source

        bus.subscribe("hit", handler)
        bus.publish("hit", damage=25, source="enemy")

        assert received == {"damage": 25, "source": "enemy"}

    def test_unsubscribe_nonexistent_raises_value_error(self) -> None:
        """Unsubscribing a callback that was never registered should raise."""
        bus = EventBus()
        import pytest

        with pytest.raises(ValueError):
            bus.unsubscribe("nope", lambda: None)

    def test_different_event_types_are_independent(self) -> None:
        """Subscribers to one event type should not receive other events."""
        bus = EventBus()
        results_a = []
        results_b = []
        bus.subscribe("event_a", lambda: results_a.append(1))
        bus.subscribe("event_b", lambda: results_b.append(2))

        bus.publish("event_a")

        assert results_a == [1]
        assert results_b == []
