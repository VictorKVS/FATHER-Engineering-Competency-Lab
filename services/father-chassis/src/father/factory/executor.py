from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from father.core.access_control import ResourceContext, SubjectContext
from father.core.contracts import ExecutionRequest
from father.factory.agent_factory import AgentFactory
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner
from father.factory.solution_factory import CustomerSolutionFactory


@dataclass(frozen=True, slots=True)
class FactoryExecutionResult:
    status: str
    agent_id: str
    build_plan: dict[str, Any]
    output: str
    trace_id: str
    workflow_id: str
    evidence: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "agent_id": self.agent_id,
            "build_plan": self.build_plan,
            "output": self.output,
            "trace_id": self.trace_id,
            "workflow_id": self.workflow_id,
            "evidence": self.evidence,
        }


class FactoryExecutor:
    """Builds a qualified profile from requirements, then executes it on ChassisRuntime."""

    def __init__(
        self,
        *,
        runtime,
        planner: RequirementPlanner,
        agent_factory: AgentFactory,
    ) -> None:
        self.runtime = runtime
        self.planner = planner
        self.agent_factory = agent_factory
        self.solution_factory = CustomerSolutionFactory(planner, agent_factory)

    def execute(
        self,
        *,
        requirement: CustomerRequirement,
        user_input: str,
        subject: SubjectContext | None = None,
        resource: ResourceContext | None = None,
        permission: str = "execute:analysis",
    ) -> FactoryExecutionResult:
        solution = self.solution_factory.plan(requirement)
        if not solution["ready"]:
            raise ValueError(f"solution not executable: {solution['status']}")

        req_plan = self.planner.plan(requirement)
        profile = self.agent_factory.build(req_plan.agent_manifest)

        metadata: dict[str, Any] = {
            "agent_id": profile.agent_id,
            "role": "agent",
            "factory_requirement_id": requirement.requirement_id,
        }
        if subject is not None or resource is not None:
            if subject is None or resource is None:
                raise ValueError("subject and resource must be provided together")
            metadata["subject_context"] = subject
            metadata["resource_context"] = resource
            metadata["permission"] = permission

        result = self.runtime.run(
            ExecutionRequest(
                input=user_input,
                metadata=metadata,
            )
        )

        return FactoryExecutionResult(
            status="EXECUTED",
            agent_id=profile.agent_id,
            build_plan=profile.build_plan.to_dict(),
            output=result.output,
            trace_id=result.trace.trace_id,
            workflow_id=result.trace.workflow_id,
            evidence=result.evidence,
        )
