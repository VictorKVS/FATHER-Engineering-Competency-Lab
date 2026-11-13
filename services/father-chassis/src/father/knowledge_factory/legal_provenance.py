from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4

from father.knowledge_factory.source_intake import SourceIntakeRecord


@dataclass(frozen=True, slots=True)
class SourceUsePolicy:
    policy_id: str
    version: str
    allowed_rights: frozenset[str]
    denied_rights: frozenset[str]
    allowed_access: frozenset[str]
    required_evidence_types: frozenset[str] = frozenset()
    allowed_use: tuple[str, ...] = ("knowledge_processing",)


@dataclass(frozen=True, slots=True)
class PolicyEvidence:
    evidence_id: str
    evidence_type: str
    authority: str
    locator: str
    evidence_hash: str


@dataclass(frozen=True, slots=True)
class SourceAdmissibilityDecision:
    decision_id: str
    source_id: str
    status: str
    policy_id: str
    policy_version: str
    allowed_use: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    provenance_id: str
    source_id: str
    source_locator: str
    source_version: str
    source_content_hash: str | None
    admissibility_decision_id: str
    evidence_refs: tuple[str, ...]
    issuer: str
    created_at: str


class LegalAccessEvaluator:
    def evaluate(
        self,
        *,
        intake: SourceIntakeRecord,
        policy: SourceUsePolicy,
        evidence: Iterable[PolicyEvidence] = (),
        issuer: str = "FATHER-KNOWLEDGE-FACTORY",
    ) -> tuple[SourceAdmissibilityDecision, ProvenanceRecord]:
        rights = intake.declared_rights.strip()
        access = intake.declared_access.strip()
        evidence_items = tuple(evidence)
        evidence_types = {item.evidence_type for item in evidence_items}
        evidence_refs = tuple(
            f"{item.evidence_id}:{item.evidence_hash}"
            for item in evidence_items
        )

        reasons: list[str] = []
        status = "HOLD"
        allowed_use: tuple[str, ...] = ()

        if rights in policy.denied_rights:
            status = "REJECTED"
            reasons.append(f"right denied by policy: {rights}")
        elif access not in policy.allowed_access:
            status = "HOLD"
            reasons.append(f"access not allowed by policy: {access}")
        elif rights not in policy.allowed_rights:
            status = "HOLD"
            reasons.append(f"right not explicitly allowed by policy: {rights}")
        else:
            missing = sorted(policy.required_evidence_types - evidence_types)
            if missing:
                status = "HOLD"
                reasons.append(
                    "missing required evidence types: " + ", ".join(missing)
                )
            elif not evidence_refs:
                status = "HOLD"
                reasons.append("approval requires policy evidence")
            elif intake.content_hash is None:
                status = "HOLD"
                reasons.append("approval requires source content hash")
            else:
                status = "APPROVED"
                allowed_use = policy.allowed_use

        decision = SourceAdmissibilityDecision(
            decision_id=f"DEC-{uuid4()}",
            source_id=intake.source_id,
            status=status,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            allowed_use=allowed_use,
            evidence_refs=evidence_refs,
            reasons=tuple(reasons),
        )

        provenance = ProvenanceRecord(
            provenance_id=f"PRV-{uuid4()}",
            source_id=intake.source_id,
            source_locator=intake.locator,
            source_version=intake.version,
            source_content_hash=intake.content_hash,
            admissibility_decision_id=decision.decision_id,
            evidence_refs=evidence_refs,
            issuer=issuer,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return decision, provenance


def verify_provenance_binding(
    intake: SourceIntakeRecord,
    decision: SourceAdmissibilityDecision,
    provenance: ProvenanceRecord,
) -> tuple[str, ...]:
    errors: list[str] = []
    if decision.source_id != intake.source_id:
        errors.append("decision source_id mismatch")
    if provenance.source_id != intake.source_id:
        errors.append("provenance source_id mismatch")
    if provenance.source_locator != intake.locator:
        errors.append("provenance locator mismatch")
    if provenance.source_version != intake.version:
        errors.append("provenance version mismatch")
    if provenance.source_content_hash != intake.content_hash:
        errors.append("provenance content_hash mismatch")
    if provenance.admissibility_decision_id != decision.decision_id:
        errors.append("provenance decision_id mismatch")
    if decision.status == "APPROVED":
        if not decision.allowed_use:
            errors.append("approved decision missing allowed_use")
        if not decision.evidence_refs:
            errors.append("approved decision missing evidence_refs")
    return tuple(errors)
