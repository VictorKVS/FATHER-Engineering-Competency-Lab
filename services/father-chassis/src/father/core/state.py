from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any, Protocol
import json
import sqlite3
from pathlib import Path


class StateStore(Protocol):
    def set(self, namespace: str, key: str, value: Any) -> None: ...
    def get(self, namespace: str, key: str, default: Any = None) -> Any: ...
    def snapshot(self, namespace: str) -> dict[str, Any]: ...


class InMemoryStateStore:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def set(self, namespace: str, key: str, value: Any) -> None:
        with self._lock:
            self._data.setdefault(namespace, {})[key] = deepcopy(value)

    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        with self._lock:
            return deepcopy(self._data.get(namespace, {}).get(key, default))

    def snapshot(self, namespace: str) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._data.get(namespace, {}))


class SQLiteStateStore:
    """Durable reference store. Re-opening the same DB restores workflow state."""
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS state (namespace TEXT, key TEXT, value TEXT NOT NULL, PRIMARY KEY(namespace,key))")

    def set(self, namespace: str, key: str, value: Any) -> None:
        raw = json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO state(namespace,key,value) VALUES(?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value=excluded.value", (namespace,key,raw))

    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT value FROM state WHERE namespace=? AND key=?", (namespace,key)).fetchone()
        return default if row is None else json.loads(row[0])

    def snapshot(self, namespace: str) -> dict[str, Any]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT key,value FROM state WHERE namespace=?", (namespace,)).fetchall()
        return {k: json.loads(v) for k,v in rows}
