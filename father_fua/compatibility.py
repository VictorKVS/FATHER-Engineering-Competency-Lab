from __future__ import annotations

from dataclasses import dataclass


VALID_STATUSES = {"PASS", "FAIL", "UNKNOWN"}


@dataclass(frozen=True)
class CompatibilityRecord:
    parts: tuple[str, ...]
    status: str
    evidence_id: str | None = None
    reason: str = ""


class CompatibilityMatrix:
    def __init__(self) -> None:
        self._records: dict[tuple[str, ...], CompatibilityRecord] = {}

    def record(
        self,
        *parts: str,
        status: str,
        evidence_id: str | None = None,
        reason: str = "",
    ) -> None:
        if not parts or any(not p for p in parts):
            raise ValueError("compatibility parts must be non-empty")
        if status not in VALID_STATUSES:
            raise ValueError("invalid compatibility status")
        self._records[tuple(parts)] = CompatibilityRecord(
            tuple(parts),
            status,
            evidence_id,
            reason,
        )

    def approve(self, *parts: str, evidence_id: str | None = None) -> None:
        self.record(*parts, status="PASS", evidence_id=evidence_id)

    def reject(self, *parts: str, evidence_id: str | None = None, reason: str = "") -> None:
        self.record(*parts, status="FAIL", evidence_id=evidence_id, reason=reason)

    def status(self, *parts: str) -> str:
        record = self._records.get(tuple(parts))
        return record.status if record else "UNKNOWN"

    def evidence_id(self, *parts: str) -> str | None:
        record = self._records.get(tuple(parts))
        return record.evidence_id if record else None

    def is_approved(self, *parts: str) -> bool:
        return self.status(*parts) == "PASS"
