from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SourceCandidate:
    source_id: str | None
    source_class: str
    title: str
    locator: str
    version: str | None = None
    publication_date: str | None = None
    effective_date: str | None = None
    content_bytes: bytes | None = None
    declared_access: str = "UNKNOWN"
    declared_rights: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class SourceIntakeRecord:
    source_id: str
    source_class: str
    title: str
    locator: str
    version: str
    publication_date: str | None
    effective_date: str | None
    content_hash: str | None
    hash_algorithm: str | None
    declared_access: str
    declared_rights: str
    duplicate_of_source_id: str | None
    status: str


@dataclass(frozen=True, slots=True)
class SourceIntakeDecision:
    accepted: bool
    record: SourceIntakeRecord | None
    reasons: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class SourceIntakeRegistry(Protocol):
    def get(self, source_id: str) -> SourceIntakeRecord | None: ...
    def find_by_hash(self, content_hash: str) -> tuple[SourceIntakeRecord, ...]: ...
    def add(self, record: SourceIntakeRecord) -> None: ...


class InMemorySourceIntakeRegistry:
    def __init__(self) -> None:
        self._records: dict[str, SourceIntakeRecord] = {}
        self._hash_index: dict[str, list[str]] = {}

    def get(self, source_id: str) -> SourceIntakeRecord | None:
        return self._records.get(source_id)

    def find_by_hash(self, content_hash: str) -> tuple[SourceIntakeRecord, ...]:
        return tuple(
            self._records[source_id]
            for source_id in self._hash_index.get(content_hash, ())
        )

    def add(self, record: SourceIntakeRecord) -> None:
        if record.source_id in self._records:
            raise ValueError(f"duplicate source_id: {record.source_id}")
        self._records[record.source_id] = record
        if record.content_hash is not None:
            self._hash_index.setdefault(record.content_hash, []).append(record.source_id)


class SourceIntakeService:
    def __init__(self, registry: SourceIntakeRegistry) -> None:
        self.registry = registry

    @staticmethod
    def _normalized_required(value: str, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} is required")
        return normalized

    def intake(self, candidate: SourceCandidate) -> SourceIntakeDecision:
        reasons: list[str] = []
        try:
            source_class = self._normalized_required(candidate.source_class, "source_class")
            title = self._normalized_required(candidate.title, "title")
            locator = self._normalized_required(candidate.locator, "locator")
        except ValueError as exc:
            return SourceIntakeDecision(False, None, (str(exc),))

        source_id = (
            candidate.source_id.strip()
            if candidate.source_id is not None and candidate.source_id.strip()
            else f"SRC-{uuid4()}"
        )
        version = (
            candidate.version.strip()
            if candidate.version is not None and candidate.version.strip()
            else "UNKNOWN"
        )

        content_hash: str | None = None
        hash_algorithm: str | None = None
        duplicate_of_source_id: str | None = None
        status = "RECEIVED"

        if candidate.content_bytes is not None:
            content_hash = sha256(candidate.content_bytes).hexdigest()
            hash_algorithm = "sha256"
            status = "FINGERPRINTED"
            duplicates = self.registry.find_by_hash(content_hash)
            if duplicates:
                duplicate_of_source_id = duplicates[0].source_id
                reasons.append(f"duplicate content of {duplicate_of_source_id}")

        record = SourceIntakeRecord(
            source_id=source_id,
            source_class=source_class,
            title=title,
            locator=locator,
            version=version,
            publication_date=candidate.publication_date,
            effective_date=candidate.effective_date,
            content_hash=content_hash,
            hash_algorithm=hash_algorithm,
            declared_access=candidate.declared_access.strip() or "UNKNOWN",
            declared_rights=candidate.declared_rights.strip() or "UNKNOWN",
            duplicate_of_source_id=duplicate_of_source_id,
            status="INTAKE_READY",
        )

        try:
            self.registry.add(record)
        except ValueError as exc:
            return SourceIntakeDecision(False, None, (str(exc),))

        evidence_refs = (
            (f"sha256:{content_hash}",)
            if content_hash is not None
            else ()
        )
        return SourceIntakeDecision(
            accepted=True,
            record=record,
            reasons=tuple(reasons),
            evidence_refs=evidence_refs,
        )
