from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    kind: str
    payload: dict
    sha256: str


def create_evidence(evidence_id: str, kind: str, payload: dict) -> Evidence:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return Evidence(evidence_id, kind, payload, hashlib.sha256(raw).hexdigest())


def verify_evidence(e: Evidence) -> bool:
    return create_evidence(e.evidence_id,e.kind,e.payload).sha256 == e.sha256
