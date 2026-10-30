from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


class FactoryEventLogger:
    def __init__(self, root: str | Path = ".father/events") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        *,
        session_id: str,
        stage_id: str,
        source: str,
        event_type: str,
        action: str,
        status: str,
        project_id: str | None = None,
        actor: str = "SYSTEM",
        target: str | None = None,
        details: dict[str, Any] | None = None,
        parent_event_id: str | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "project_id": project_id,
            "stage_id": stage_id,
            "source": source,
            "event_type": event_type,
            "action": action,
            "status": status,
            "actor": actor,
            "target": target,
            "details": details or {},
            "parent_event_id": parent_event_id,
            "correlation_id": correlation_id,
        }
        path = self.root / f"{session_id}.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def read_session(self, session_id: str) -> list[dict[str, Any]]:
        path = self.root / f"{session_id}.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
