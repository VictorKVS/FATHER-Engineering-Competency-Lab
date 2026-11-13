from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
import json

from .models import EvidenceRecord


def _canonical(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


class EvidenceLedger:
    """Append-only, hash-linked in-memory ledger core.

    Persistence/signatures are adapters. The core only defines deterministic record linkage.
    """

    def __init__(self) -> None:
        self._records: list[EvidenceRecord] = []

    def append(self, record: EvidenceRecord) -> EvidenceRecord:
        if any(x.evidence_id == record.evidence_id for x in self._records):
            raise ValueError(f"duplicate evidence_id: {record.evidence_id}")

        parent = self._records[-1].record_hash if self._records else None
        payload = asdict(record)
        payload["parent_evidence_hash"] = parent
        payload["record_hash"] = None
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()

        linked = replace(
            record,
            parent_evidence_hash=parent,
            record_hash=digest,
        )
        self._records.append(linked)
        return linked

    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._records)

    def verify(self) -> bool:
        parent = None
        for record in self._records:
            if record.parent_evidence_hash != parent:
                return False
            payload = asdict(record)
            expected = payload.pop("record_hash")
            payload["record_hash"] = None
            actual = sha256(_canonical(payload).encode("utf-8")).hexdigest()
            if actual != expected:
                return False
            parent = record.record_hash
        return True
