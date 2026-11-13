from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Subject:
    subject_id: str
    subject_type: str
    name: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    subject_id: str
    domain: str
    capability: str
    claimed_level: str
    status: str = "UNQUALIFIED"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    subject_id: str
    claim_id: str
    evidence_type: str
    artifact_ref: str
    artifact_hash: str
    observed_at: str
    issuer: str
    source_commit: str | None = None
    signature_ref: str | None = None
    parent_evidence_hash: str | None = None
    record_hash: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class QualificationDecision:
    qualification_id: str
    subject_id: str
    claim_id: str
    requested_level: str
    qualified: bool
    evidence_ids: tuple[str, ...]
    reasons: tuple[str, ...]
