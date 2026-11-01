from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    payload_json: str
    sha256: str


def create_snapshot(snapshot_id: str, payload: dict) -> Snapshot:
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return Snapshot(snapshot_id,raw,digest)


def verify_snapshot(snapshot: Snapshot) -> bool:
    digest=hashlib.sha256(snapshot.payload_json.encode("utf-8")).hexdigest()
    return digest==snapshot.sha256


def restore_snapshot(snapshot: Snapshot) -> dict:
    if not verify_snapshot(snapshot):
        raise ValueError("snapshot integrity failure")
    return json.loads(snapshot.payload_json)
