from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

try:
    from trust_competency import (
        Claim,
        CompetencyEvaluator,
        CompetencyPolicy,
        EvidenceRecord,
        QualificationDecision,
    )
except ImportError:  # pragma: no cover - environment gate, not a runtime bypass
    Claim = None  # type: ignore[assignment]
    EvidenceRecord = None  # type: ignore[assignment]
    QualificationDecision = None  # type: ignore[assignment]
    CompetencyEvaluator = None  # type: ignore[assignment]
    CompetencyPolicy = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class StageCompetencyPolicy:
    stage_id: str
    domain: str
    capability: str
    minimum_level: str
    minimum_evidence_count: int
    required_evidence_types: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class CompetencyAdmissionRequest:
    workflow_id: str
    stage_id: str
    agent_id: str


@dataclass(frozen=True, slots=True)
class CompetencyAdmissionDecision:
    workflow_id: str
    stage_id: str
    agent_id: str
    admitted: bool
    requested_level: str
    trust_qualification_id: str | None
    evidence_ids: tuple[str, ...]
    reasons: tuple[str, ...]


class TrustCompetencySource(Protocol):
    def get_claim(self, agent_id: str, domain: str, capability: str): ...
    def get_evidence(self, agent_id: str, claim_id: str): ...


class InMemoryTrustCompetencySource:
    def __init__(self, claims=(), evidence=()) -> None:
        self._claims = tuple(claims)
        self._evidence = tuple(evidence)

    def get_claim(self, agent_id: str, domain: str, capability: str):
        for claim in self._claims:
            if (
                claim.subject_id == agent_id
                and claim.domain == domain
                and claim.capability == capability
            ):
                return claim
        return None

    def get_evidence(self, agent_id: str, claim_id: str):
        return tuple(
            item for item in self._evidence
            if item.subject_id == agent_id and item.claim_id == claim_id
        )


class CompetencyAdmissionGate:
    def __init__(
        self,
        *,
        source: TrustCompetencySource,
        policies: tuple[StageCompetencyPolicy, ...],
    ) -> None:
        self.source = source
        self._policies = {item.stage_id: item for item in policies}
        if len(self._policies) != len(policies):
            raise ValueError("duplicate competency policy stage_id")

    def evaluate(self, request: CompetencyAdmissionRequest) -> CompetencyAdmissionDecision:
        policy = self._policies.get(request.stage_id)
        if policy is None:
            return CompetencyAdmissionDecision(
                workflow_id=request.workflow_id,
                stage_id=request.stage_id,
                agent_id=request.agent_id,
                admitted=False,
                requested_level="UNKNOWN",
                trust_qualification_id=None,
                evidence_ids=(),
                reasons=(f"unknown competency policy for stage {request.stage_id}",),
            )

        if CompetencyEvaluator is None or CompetencyPolicy is None:
            return CompetencyAdmissionDecision(
                workflow_id=request.workflow_id,
                stage_id=request.stage_id,
                agent_id=request.agent_id,
                admitted=False,
                requested_level=policy.minimum_level,
                trust_qualification_id=None,
                evidence_ids=(),
                reasons=("trust_competency package is unavailable",),
            )

        claim = self.source.get_claim(
            request.agent_id,
            policy.domain,
            policy.capability,
        )
        if claim is None:
            return CompetencyAdmissionDecision(
                workflow_id=request.workflow_id,
                stage_id=request.stage_id,
                agent_id=request.agent_id,
                admitted=False,
                requested_level=policy.minimum_level,
                trust_qualification_id=None,
                evidence_ids=(),
                reasons=(
                    f"no competency claim for {policy.domain}/{policy.capability}",
                ),
            )

        evidence = self.source.get_evidence(request.agent_id, claim.claim_id)
        trust_policy = CompetencyPolicy(
            level=policy.minimum_level,
            minimum_evidence_count=policy.minimum_evidence_count,
            required_evidence_types=policy.required_evidence_types,
        )
        result = CompetencyEvaluator().qualify(
            claim=claim,
            evidence=evidence,
            policy=trust_policy,
        )

        return CompetencyAdmissionDecision(
            workflow_id=request.workflow_id,
            stage_id=request.stage_id,
            agent_id=request.agent_id,
            admitted=bool(result.qualified),
            requested_level=policy.minimum_level,
            trust_qualification_id=result.qualification_id,
            evidence_ids=tuple(result.evidence_ids),
            reasons=tuple(result.reasons),
        )


def build_reference_stage_competency_policies() -> tuple[StageCompetencyPolicy, ...]:
    return (
        StageCompetencyPolicy(
            stage_id="BUSINESS_ANALYSIS",
            domain="business_analysis",
            capability="process_design",
            minimum_level="C3",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="SYSTEM_ANALYSIS",
            domain="system_analysis",
            capability="requirements_engineering",
            minimum_level="C4",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="ALGORITHM_SELECTION",
            domain="algorithm_engineering",
            capability="algorithm_selection",
            minimum_level="C4",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"benchmark", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="ARCHITECTURE",
            domain="ai_architecture",
            capability="system_design",
            minimum_level="C5",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="TEST_ARCHITECTURE",
            domain="test_engineering",
            capability="test_architecture",
            minimum_level="C4",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="DEVELOPMENT_PACKET",
            domain="ai_architecture",
            capability="engineering_governance",
            minimum_level="C5",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"architecture", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="IMPLEMENTATION",
            domain="software_engineering",
            capability="contract_implementation",
            minimum_level="C4",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="DELIVERY",
            domain="devsecops",
            capability="secure_delivery",
            minimum_level="C4",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"implementation", "qualification"}),
        ),
        StageCompetencyPolicy(
            stage_id="QUALIFICATION",
            domain="qualification",
            capability="evidence_audit",
            minimum_level="C5",
            minimum_evidence_count=2,
            required_evidence_types=frozenset({"audit", "qualification"}),
        ),
    )
