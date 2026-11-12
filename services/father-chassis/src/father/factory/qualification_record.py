from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class FactoryQualificationRecord:
    qualification_id: str
    created_at: str
    requirement_id: str
    agent_id: str
    build_plan: dict[str, Any]
    trace_id: str
    workflow_id: str
    evidence_hashes: tuple[str, ...]
    policy_decisions: tuple[dict[str, Any], ...]
    provider_bindings: tuple[dict[str, Any], ...]
    audit_event_count: int
    result_status: str
    qualified: bool
    record_hash: str

    @classmethod
    def from_execution(cls, *, requirement_id: str, execution_result, audit_events) -> "FactoryQualificationRecord":
        evidence_hashes = tuple(
            sorted({
                str(item.get("content_hash"))
                for item in execution_result.evidence
                if item.get("content_hash")
            })
        )
        policy_decisions = tuple(
            event.payload
            for event in audit_events
            if event.type in {"access.decision", "policy.decision"}
        )
        provider_bindings = tuple(execution_result.build_plan.get("provider_bindings", []))

        payload = {
            "created_at": _utcnow(),
            "requirement_id": requirement_id,
            "agent_id": execution_result.agent_id,
            "build_plan": execution_result.build_plan,
            "trace_id": execution_result.trace_id,
            "workflow_id": execution_result.workflow_id,
            "evidence_hashes": evidence_hashes,
            "policy_decisions": policy_decisions,
            "provider_bindings": provider_bindings,
            "audit_event_count": len(audit_events),
            "result_status": execution_result.status,
            "qualified": bool(
                execution_result.status == "EXECUTED"
                and evidence_hashes
                and len(audit_events) >= 2
            ),
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return cls(
            qualification_id=f"FQ-{digest[:16]}",
            created_at=payload["created_at"],
            requirement_id=requirement_id,
            agent_id=execution_result.agent_id,
            build_plan=execution_result.build_plan,
            trace_id=execution_result.trace_id,
            workflow_id=execution_result.workflow_id,
            evidence_hashes=evidence_hashes,
            policy_decisions=policy_decisions,
            provider_bindings=provider_bindings,
            audit_event_count=len(audit_events),
            result_status=execution_result.status,
            qualified=payload["qualified"],
            record_hash=digest,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
