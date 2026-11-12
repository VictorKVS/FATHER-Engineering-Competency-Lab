from __future__ import annotations

from dataclasses import asdict
from typing import Any

from father.factory.agent_factory import AgentFactory
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


class CustomerSolutionFactory:
    def __init__(self, planner: RequirementPlanner, agent_factory: AgentFactory) -> None:
        self.planner = planner
        self.agent_factory = agent_factory

    def plan(self, requirement: CustomerRequirement) -> dict[str, Any]:
        req_plan = self.planner.plan(requirement)
        if not req_plan.complete:
            return {
                "requirement": req_plan.to_dict(),
                "build": None,
                "ready": False,
                "status": "REQUIREMENTS_UNRESOLVED",
            }

        build = self.agent_factory.plan(req_plan.agent_manifest)
        return {
            "requirement": req_plan.to_dict(),
            "build": build.to_dict(),
            "ready": build.buildable,
            "status": "READY_TO_BUILD" if build.buildable else "BUILD_BLOCKED",
        }
