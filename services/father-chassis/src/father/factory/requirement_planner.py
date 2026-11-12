from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from father.core.agent_manifest import AgentManifest


@dataclass(frozen=True, slots=True)
class CustomerRequirement:
    requirement_id: str
    title: str
    needs: frozenset[str]
    constraints: frozenset[str] = frozenset()
    required_permissions: frozenset[str] = frozenset()
    approval_required_for: frozenset[str] = frozenset()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RequirementPlan:
    requirement_id: str
    agent_manifest: AgentManifest
    unresolved_needs: tuple[str, ...]
    rationale: dict[str, str]

    @property
    def complete(self) -> bool:
        return not self.unresolved_needs

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "complete": self.complete,
            "unresolved_needs": list(self.unresolved_needs),
            "rationale": dict(self.rationale),
            "agent_manifest": {
                "agent_id": self.agent_manifest.agent_id,
                "version": self.agent_manifest.version,
                "capabilities": sorted(self.agent_manifest.capabilities),
                "required_permissions": sorted(self.agent_manifest.required_permissions),
                "required_providers": sorted(self.agent_manifest.required_providers),
                "approval_required_for": sorted(self.agent_manifest.approval_required_for),
                "max_steps": self.agent_manifest.max_steps,
                "timeout_seconds": self.agent_manifest.timeout_seconds,
                "max_cost_usd": self.agent_manifest.max_cost_usd,
            },
        }


DEFAULT_NEED_MAP: dict[str, frozenset[str]] = {
    "analyze_documents": frozenset({"knowledge.retrieve", "model.generate", "evidence.trace"}),
    "create_report": frozenset({"report.create", "audit.write"}),
    "enforce_policy": frozenset({"policy.enforce"}),
    "trace_decisions": frozenset({"decision.trace"}),
    "run_workflow": frozenset({"workflow.execute", "agent.execute"}),
}


class RequirementPlanner:
    """Deterministic first-stage planner from customer needs to an AgentManifest."""

    def __init__(self, need_map: dict[str, frozenset[str]] | None = None) -> None:
        self.need_map = dict(need_map or DEFAULT_NEED_MAP)

    def plan(self, requirement: CustomerRequirement) -> RequirementPlan:
        capabilities: set[str] = set()
        unresolved: list[str] = []
        rationale: dict[str, str] = {}

        for need in sorted(requirement.needs):
            mapped = self.need_map.get(need)
            if mapped is None:
                unresolved.append(need)
                continue
            capabilities.update(mapped)
            rationale[need] = ", ".join(sorted(mapped))

        manifest = AgentManifest(
            agent_id=requirement.metadata.get(
                "agent_id",
                requirement.requirement_id.lower().replace("_", "-"),
            ),
            version=requirement.metadata.get("agent_version", "0.1.0"),
            capabilities=frozenset(capabilities),
            required_permissions=requirement.required_permissions,
            approval_required_for=requirement.approval_required_for,
            max_steps=int(requirement.metadata.get("max_steps", "12")),
            timeout_seconds=int(requirement.metadata.get("timeout_seconds", "120")),
            max_cost_usd=(
                float(requirement.metadata["max_cost_usd"])
                if "max_cost_usd" in requirement.metadata
                else None
            ),
            metadata={
                "requirement_id": requirement.requirement_id,
                "title": requirement.title,
            },
        )
        return RequirementPlan(
            requirement_id=requirement.requirement_id,
            agent_manifest=manifest,
            unresolved_needs=tuple(unresolved),
            rationale=rationale,
        )
