from __future__ import annotations

from dataclasses import dataclass

from .models import Claim, EvidenceRecord, QualificationDecision


LEVEL_ORDER = {
    "C0": 0,
    "C1": 1,
    "C2": 2,
    "C3": 3,
    "C4": 4,
    "C5": 5,
    "C6": 6,
}


@dataclass(frozen=True, slots=True)
class CompetencyPolicy:
    level: str
    minimum_evidence_count: int
    required_evidence_types: frozenset[str] = frozenset()


class CompetencyEvaluator:
    """Evidence-based evaluator shared by PERSON and PRODUCT subjects."""

    def qualify(
        self,
        *,
        claim: Claim,
        evidence: tuple[EvidenceRecord, ...],
        policy: CompetencyPolicy,
    ) -> QualificationDecision:
        reasons: list[str] = []
        relevant = tuple(
            item for item in evidence
            if item.subject_id == claim.subject_id and item.claim_id == claim.claim_id
        )

        if policy.level not in LEVEL_ORDER:
            reasons.append(f"unknown policy level: {policy.level}")
        if claim.claimed_level not in LEVEL_ORDER:
            reasons.append(f"unknown claimed level: {claim.claimed_level}")
        elif policy.level in LEVEL_ORDER and LEVEL_ORDER[claim.claimed_level] < LEVEL_ORDER[policy.level]:
            reasons.append(
                f"claimed level {claim.claimed_level} is below requested qualification {policy.level}"
            )

        if len(relevant) < policy.minimum_evidence_count:
            reasons.append(
                f"evidence count {len(relevant)} < required {policy.minimum_evidence_count}"
            )

        observed_types = {item.evidence_type for item in relevant}
        missing = sorted(policy.required_evidence_types - observed_types)
        if missing:
            reasons.append("missing evidence types: " + ",".join(missing))

        qualified = not reasons
        return QualificationDecision(
            qualification_id=f"QUAL-{claim.claim_id}-{policy.level}",
            subject_id=claim.subject_id,
            claim_id=claim.claim_id,
            requested_level=policy.level,
            qualified=qualified,
            evidence_ids=tuple(item.evidence_id for item in relevant),
            reasons=tuple(reasons),
        )
