from __future__ import annotations

from dataclasses import dataclass

from .contracts import ExecutionRequest, TraceContext


@dataclass(frozen=True, slots=True)
class WorkflowPlan:
    name: str
    action: str = "create_report"
    use_rag: bool = True


class WorkflowEngine:
    def __init__(self) -> None:
        self._plans: dict[str, WorkflowPlan] = {
            "default": WorkflowPlan(name="default", action="create_report", use_rag=True),
            "model_only": WorkflowPlan(name="model_only", action="create_report", use_rag=False),
        }

    def register(self, plan: WorkflowPlan) -> None:
        self._plans[plan.name] = plan

    def plan(self, name: str, req: ExecutionRequest, trace: TraceContext) -> WorkflowPlan:
        del req, trace
        try:
            return self._plans[name]
        except KeyError as exc:
            raise ValueError(f"unknown workflow: {name}") from exc
