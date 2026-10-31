from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import sys
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
        event_id: str | None = None,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_id": event_id or str(uuid.uuid4()),
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
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


def desktop_trace_dir() -> Path:
    """Return the user's real Desktop folder and ensure Desktop/Фабрика exists."""
    desktop: Path | None = None
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            # CSIDL_DESKTOPDIRECTORY = 0x0010
            if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf) == 0:
                desktop = Path(buf.value)
        except Exception:
            desktop = None
    if desktop is None:
        desktop = Path.home() / "Desktop"
    target = desktop / "Фабрика"
    target.mkdir(parents=True, exist_ok=True)
    return target


def export_trace_file(
    *,
    session_id: str,
    runtime_events: list[dict[str, Any]],
    ui_events: list[dict[str, Any]] | None = None,
    page: str | None = None,
) -> Path:
    ui_events = ui_events or []
    merged = sorted(
        _dedupe_events([*ui_events, *runtime_events]),
        key=lambda e: str(e.get("timestamp", "")),
    )
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    path = desktop_trace_dir() / f"NEXUS_TRACE_{stamp}.json"
    payload = {
        "schema": "NEXUS_FACTORY_TRACE_EXPORT_V1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "page": page,
        "ui_event_count": len(ui_events),
        "runtime_event_count": len(runtime_events),
        "total_event_count": len(merged),
        "events": merged,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def next_daily_trace_number(target_dir: Path | None = None) -> tuple[str, int]:
    target_dir = target_dir or desktop_trace_dir()
    date_str = datetime.now().astimezone().strftime("%Y-%m-%d")
    prefix = f"NEXUS_TRACE_{date_str}_"
    highest = 0
    for path in target_dir.glob(f"{prefix}*.json"):
        stem = path.stem
        try:
            suffix = stem.rsplit("_", 1)[1]
            highest = max(highest, int(suffix))
        except Exception:
            continue
    return date_str, highest + 1


def reserve_trace_file(session_id: str) -> Path:
    target = desktop_trace_dir()
    date_str, number = next_daily_trace_number(target)
    path = target / f"NEXUS_TRACE_{date_str}_{number:03d}.json"
    payload = {
        "schema": "NEXUS_FACTORY_TRACE_EXPORT_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "trace_number": number,
        "trace_date": date_str,
        "status": "ACTIVE",
        "events": [],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _dedupe_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for event in events:
        event_id = str(event.get("event_id") or "")
        if event_id and event_id in seen:
            continue
        if event_id:
            seen.add(event_id)
        result.append(event)
    return result


def append_trace_snapshot(
    *,
    trace_path: str | Path,
    session_id: str,
    runtime_events: list[dict[str, Any]],
    ui_events: list[dict[str, Any]] | None = None,
    page: str | None = None,
    status: str = "ACTIVE",
) -> Path:
    path = Path(trace_path)
    ui_events = ui_events or []
    merged = sorted(
        [*ui_events, *runtime_events],
        key=lambda e: str(e.get("timestamp", "")),
    )
    payload = {
        "schema": "NEXUS_FACTORY_TRACE_EXPORT_V1",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "page": page,
        "status": status,
        "ui_event_count": len(ui_events),
        "runtime_event_count": len(runtime_events),
        "total_event_count": len(merged),
        "events": merged,
    }
    try:
        existing=json.loads(path.read_text(encoding="utf-8"))
        payload["trace_number"]=existing.get("trace_number")
        payload["trace_date"]=existing.get("trace_date")
        payload["created_at"]=existing.get("created_at")
    except Exception:
        pass
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
