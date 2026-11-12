from __future__ import annotations

from .approval import HumanApprovalGate
from .audit import AuditStore
from .config import ChassisConfig
from .contracts import Event, ExecutionRequest, ExecutionResult, Guardrail, RagAdapter, TraceContext
from .control import EmergencyStop
from .event_bus import EventBus
from .evidence import normalize_evidence
from .metrics import Metrics
from .model_router import ModelRouter
from .registry import BlockRegistry
from .resilience import call_with_retry_timeout
from .state import StateStore
from .tool_registry import ToolRegistry
from .tracing import Tracer
from .workflow import WorkflowEngine


class ChassisRuntime:
    def __init__(
        self,
        *,
        config: ChassisConfig,
        models: ModelRouter,
        rag: RagAdapter,
        guardrail: Guardrail,
        audit: AuditStore,
        metrics: Metrics,
        event_bus: EventBus,
        state: StateStore,
        workflows: WorkflowEngine,
        registry: BlockRegistry,
        emergency_stop: EmergencyStop,
        tools: ToolRegistry,
        approval_gate: HumanApprovalGate,
        tracer: Tracer,
        default_tool: str = "default",
    ) -> None:
        self.config = config
        self.models = models
        self.rag = rag
        self.guardrail = guardrail
        self.audit = audit
        self.metrics = metrics
        self.event_bus = event_bus
        self.state = state
        self.workflows = workflows
        self.registry = registry
        self.emergency_stop = emergency_stop
        self.tools = tools
        self.approval_gate = approval_gate
        self.tracer = tracer
        self.default_tool = default_tool
        self.tool = self.tools._tools[default_tool].instance

    def _emit(self, trace: TraceContext, event_type: str, payload: dict) -> None:
        event = Event(type=event_type, trace_id=trace.trace_id, payload=payload)
        self.audit.write(event)
        self.event_bus.publish(event)

    def _resilient(self, trace: TraceContext, name: str, fn, **attrs):
        return self.tracer.record(
            name,
            trace.trace_id,
            lambda: call_with_retry_timeout(
                fn,
                attempts=self.config.retry.attempts,
                timeout_ms=self.config.retry.timeout_ms,
            ),
            **attrs,
        )

    def run(self, req: ExecutionRequest) -> ExecutionResult:
        trace = TraceContext()
        started = self.metrics.start()
        success = False
        self._emit(trace, "request.received", {"input": req.input})
        self.state.set("workflow", trace.workflow_id, {"status": "received", "trace_id": trace.trace_id})
        try:
            self.emergency_stop.ensure_running()
            self._emit(trace, "control.emergency_stop_checked", {"engaged": False})

            plan = self.workflows.plan(self.config.workflow, req, trace)
            self._emit(trace, "workflow.planned", {"workflow": plan.name, "action": plan.action})
            self.state.set("workflow", trace.workflow_id, {"status": "running", "trace_id": trace.trace_id, "workflow": plan.name})

            evidence_raw: list[dict] = []
            if plan.use_rag:
                evidence_raw = self._resilient(trace, "rag.retrieve", lambda: self.rag.retrieve(req.input, trace), adapter=self.rag.name)
                self._emit(trace, "rag.completed", {"adapter": self.rag.name, "evidence_count": len(evidence_raw)})
            evidence_items = normalize_evidence(evidence_raw)
            evidence = [item.to_dict() for item in evidence_items]

            context = "\n".join(item.text for item in evidence_items)
            prompt = f"USER: {req.input}\nEVIDENCE:\n{context}"
            requested_model = req.metadata.get("model")
            model = self.models.resolve(str(requested_model) if requested_model else None)
            self._emit(trace, "model.routed", {"adapter": model.name})
            draft = self._resilient(trace, "model.generate", lambda: model.generate(prompt, trace), adapter=model.name)
            self._emit(trace, "model.completed", {"adapter": model.name})

            allowed, reason = self.guardrail.allow(plan.action, {"draft": draft}, trace)
            self._emit(trace, "policy.decision", {"action": plan.action, "allowed": allowed, "reason": reason})
            if not allowed:
                raise PermissionError(reason)

            approval_id = req.metadata.get("approval_id")
            self.approval_gate.check(trace_id=trace.trace_id, action=plan.action, approval_id=str(approval_id) if approval_id else None)
            if plan.action in self.approval_gate.required_actions:
                self._emit(trace, "approval.accepted", {"action": plan.action, "approval_id": approval_id})

            self.emergency_stop.ensure_running()
            payload = {"draft": draft}
            tool_result = self._resilient(
                trace,
                "tool.execute",
                lambda: self.tools.execute(self.default_tool, plan.action, payload, trace, role=str(req.metadata.get("role", "agent"))),
                tool=self.default_tool,
                action=plan.action,
            )
            self._emit(trace, "tool.completed", {"adapter": self.default_tool, "action": plan.action})
            output = str(tool_result["output"])
            self.state.set("workflow", trace.workflow_id, {"status": "completed", "trace_id": trace.trace_id, "workflow": plan.name})
            self._emit(trace, "request.completed", {"status": "ok", "evidence_hashes": [e.content_hash for e in evidence_items]})
            success = True
            return ExecutionResult(output=output, trace=trace, evidence=evidence, events=self.audit.by_trace(trace.trace_id))
        except Exception as exc:
            self.state.set("workflow", trace.workflow_id, {"status": "failed", "trace_id": trace.trace_id, "error": type(exc).__name__})
            self._emit(trace, "request.failed", {"error": type(exc).__name__, "message": str(exc)})
            raise
        finally:
            self.metrics.finish(started, success)
