from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditEvent:
    seq: int
    ts: float
    kind: str
    actor: str
    correlation_id: str
    detail: dict
    prev_hash: str
    event_hash: str


class AuditLog:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    @staticmethod
    def _hash(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

    def append(self, *, kind: str, actor: str, correlation_id: str, detail: dict) -> AuditEvent:
        prev = self.events[-1].event_hash if self.events else "GENESIS"
        ts = time.time()
        payload = {
            "seq": len(self.events) + 1,
            "ts": ts,
            "kind": kind,
            "actor": actor,
            "correlation_id": correlation_id,
            "detail": detail,
            "prev_hash": prev,
        }
        ev = AuditEvent(event_hash=self._hash(payload), **payload)
        self.events.append(ev)
        return ev

    def verify(self) -> bool:
        prev = "GENESIS"
        for idx, ev in enumerate(self.events, start=1):
            payload = {
                "seq": ev.seq,
                "ts": ev.ts,
                "kind": ev.kind,
                "actor": ev.actor,
                "correlation_id": ev.correlation_id,
                "detail": ev.detail,
                "prev_hash": ev.prev_hash,
            }
            if ev.seq != idx or ev.prev_hash != prev or ev.event_hash != self._hash(payload):
                return False
            prev = ev.event_hash
        return True
