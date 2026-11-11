from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock

from .contracts import Event


class AuditStore:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def health(self) -> bool:
        return True

    def write(self, event: Event) -> None:
        self._events.append(event)

    def by_trace(self, trace_id: str) -> list[Event]:
        return [e for e in self._events if e.trace_id == trace_id]


class SQLiteAuditStore:
    """Persistent audit sink for workstation/single-node deployments."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS audit_events ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, trace_id TEXT NOT NULL, "
                "type TEXT NOT NULL, ts TEXT NOT NULL, payload TEXT NOT NULL)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_audit_trace ON audit_events(trace_id,id)")

    def health(self) -> bool:
        try:
            with sqlite3.connect(self.path) as db:
                db.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def write(self, event: Event) -> None:
        with self._lock, sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO audit_events(trace_id,type,ts,payload) VALUES(?,?,?,?)",
                (event.trace_id, event.type, event.ts, json.dumps(event.payload, ensure_ascii=False)),
            )

    def by_trace(self, trace_id: str) -> list[Event]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT type,trace_id,payload,ts FROM audit_events WHERE trace_id=? ORDER BY id",
                (trace_id,),
            ).fetchall()
        return [Event(type=t, trace_id=tr, payload=json.loads(payload), ts=ts) for t, tr, payload, ts in rows]
