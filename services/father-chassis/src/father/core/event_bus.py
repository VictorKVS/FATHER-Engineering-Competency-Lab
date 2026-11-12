from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from .contracts import Event

Subscriber = Callable[[Event], None]


class EventBus:
    """Small in-process event bus. Replaceable later by Redis/NATS/Kafka adapter."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._history: list[Event] = []

    def subscribe(self, event_type: str, handler: Subscriber) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        self._history.append(event)
        for handler in self._subscribers.get(event.type, []):
            handler(event)
        for handler in self._subscribers.get("*", []):
            handler(event)

    def by_trace(self, trace_id: str) -> list[Event]:
        return [e for e in self._history if e.trace_id == trace_id]
