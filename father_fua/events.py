from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_id: str
    correlation_id: str
    kind: str
    payload: dict
    sequence: int


class EventBus:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.dead_letters: list[Event] = []
        self._idempotency: dict[str, Event] = {}

    def publish(self, *, correlation_id: str, kind: str, payload: dict, idempotency_key: str) -> Event:
        if not idempotency_key:
            raise ValueError("idempotency key required")
        if idempotency_key in self._idempotency:
            return self._idempotency[idempotency_key]
        event = Event(
            event_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            kind=kind,
            payload=payload,
            sequence=len(self.events)+1,
        )
        self.events.append(event)
        self._idempotency[idempotency_key]=event
        return event

    def dead_letter(self, event: Event) -> None:
        self.dead_letters.append(event)
