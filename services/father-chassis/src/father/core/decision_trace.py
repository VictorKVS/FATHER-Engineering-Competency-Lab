from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class NormReference:
    source_id: str
    title: str
    requirement_id: str
    locator: str
    version: str
    effective_date: str | None = None
    source_uri: str | None = None
    source_hash: str | None = None


@dataclass(frozen=True, slots=True)
class DecisionEvidence:
    evidence_id: str
    source: str
    locator: str
    content_hash: str
    summary: str
    collected_at: str = field(default_factory=_utcnow)


@dataclass(frozen=True, slots=True)
class DecisionOption:
    option_id: str
    description: str
    benefits: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    rejected_reason: str | None = None


@dataclass(slots=True)
class DecisionStep:
    step_id: str
    trace_id: str
    stage: str
    actor_type: str
    actor_id: str
    statement: str
    norm_refs: list[NormReference] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    input_step_ids: list[str] = field(default_factory=list)
    options: list[DecisionOption] = field(default_factory=list)
    selected_option_id: str | None = None
    confidence: float | None = None
    requires_human_approval: bool = False
    approval_id: str | None = None
    timestamp: str = field(default_factory=_utcnow)
    previous_hash: str | None = None
    step_hash: str = ""

    def seal(self) -> str:
        payload = asdict(self)
        payload["step_hash"] = ""
        self.step_hash = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return self.step_hash


@dataclass(slots=True)
class DecisionTrace:
    decision_id: str
    subject: str
    domain: str
    created_at: str = field(default_factory=_utcnow)
    steps: list[DecisionStep] = field(default_factory=list)
    evidence: dict[str, DecisionEvidence] = field(default_factory=dict)

    @classmethod
    def create(cls, subject: str, domain: str) -> "DecisionTrace":
        return cls(decision_id=str(uuid4()), subject=subject, domain=domain)

    def add_evidence(self, evidence: DecisionEvidence) -> None:
        if evidence.evidence_id in self.evidence:
            raise ValueError(f"duplicate evidence_id: {evidence.evidence_id}")
        self.evidence[evidence.evidence_id] = evidence

    def add_step(
        self,
        *,
        stage: str,
        actor_type: str,
        actor_id: str,
        statement: str,
        norm_refs: list[NormReference] | None = None,
        evidence_ids: list[str] | None = None,
        input_step_ids: list[str] | None = None,
        options: list[DecisionOption] | None = None,
        selected_option_id: str | None = None,
        confidence: float | None = None,
        requires_human_approval: bool = False,
        approval_id: str | None = None,
    ) -> DecisionStep:
        evidence_ids = list(evidence_ids or [])
        missing = [eid for eid in evidence_ids if eid not in self.evidence]
        if missing:
            raise ValueError("unknown evidence ids: " + ",".join(missing))

        known_steps = {s.step_id for s in self.steps}
        bad_inputs = [sid for sid in (input_step_ids or []) if sid not in known_steps]
        if bad_inputs:
            raise ValueError("unknown input step ids: " + ",".join(bad_inputs))

        previous_hash = self.steps[-1].step_hash if self.steps else None
        step = DecisionStep(
            step_id=str(uuid4()),
            trace_id=self.decision_id,
            stage=stage,
            actor_type=actor_type,
            actor_id=actor_id,
            statement=statement,
            norm_refs=list(norm_refs or []),
            evidence_ids=evidence_ids,
            input_step_ids=list(input_step_ids or []),
            options=list(options or []),
            selected_option_id=selected_option_id,
            confidence=confidence,
            requires_human_approval=requires_human_approval,
            approval_id=approval_id,
            previous_hash=previous_hash,
        )
        step.seal()
        self.steps.append(step)
        return step

    def verify_chain(self) -> bool:
        previous = None
        for step in self.steps:
            if step.previous_hash != previous:
                return False
            expected = step.step_hash
            copy = DecisionStep(**{**asdict(step), "norm_refs": step.norm_refs, "options": step.options})
            copy.step_hash = ""
            if sha256(_canonical(asdict(copy)).encode("utf-8")).hexdigest() != expected:
                return False
            previous = expected
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "subject": self.subject,
            "domain": self.domain,
            "created_at": self.created_at,
            "evidence": {k: asdict(v) for k, v in self.evidence.items()},
            "steps": [asdict(s) for s in self.steps],
            "chain_valid": self.verify_chain(),
        }
