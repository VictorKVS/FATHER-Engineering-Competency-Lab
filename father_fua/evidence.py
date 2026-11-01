from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    kind: str
    payload: dict
    sha256: str
    provenance: str = "runtime"
    correlation_id: str | None = None
    created_at: float = 0.0


def _evidence_hash(
    evidence_id: str,
    kind: str,
    payload: dict,
    *,
    provenance: str,
    correlation_id: str | None,
    created_at: float,
) -> str:
    envelope = {
        "evidence_id": evidence_id,
        "kind": kind,
        "payload": payload,
        "provenance": provenance,
        "correlation_id": correlation_id,
        "created_at": created_at,
    }
    raw = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def create_evidence(
    evidence_id: str,
    kind: str,
    payload: dict,
    *,
    provenance: str = "runtime",
    correlation_id: str | None = None,
    created_at: float | None = None,
) -> Evidence:
    ts = time.time() if created_at is None else float(created_at)
    digest = _evidence_hash(
        evidence_id,
        kind,
        payload,
        provenance=provenance,
        correlation_id=correlation_id,
        created_at=ts,
    )
    return Evidence(
        evidence_id=evidence_id,
        kind=kind,
        payload=payload,
        sha256=digest,
        provenance=provenance,
        correlation_id=correlation_id,
        created_at=ts,
    )


def verify_evidence(e: Evidence) -> bool:
    expected = _evidence_hash(
        e.evidence_id,
        e.kind,
        e.payload,
        provenance=e.provenance,
        correlation_id=e.correlation_id,
        created_at=e.created_at,
    )
    return expected == e.sha256
