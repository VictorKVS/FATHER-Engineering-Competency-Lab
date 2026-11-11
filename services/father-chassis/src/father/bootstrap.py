from __future__ import annotations
from pathlib import Path

from father.adapters.mock import DefaultGuardrail, MockTool
from father.adapters.knowledge import SQLiteKnowledgeRag
from father.adapters.models import GroundedTemplateModel
from father.core.approval import HumanApprovalGate
from father.core.audit import AuditStore
from father.core.config import ChassisConfig, load_config
from father.core.control import EmergencyStop
from father.core.event_bus import EventBus
from father.core.metrics import Metrics
from father.core.model_router import ModelRouter
from father.core.registry import BlockDescriptor, BlockRegistry
from father.core.runtime import ChassisRuntime
from father.core.state import SQLiteStateStore, StateStore
from father.core.tool_registry import ActionSchema, ToolRegistry, ToolSpec
from father.core.tracing import Tracer
from father.core.workflow import WorkflowEngine


def build_runtime(*, denied_actions: set[str] | None = None, config: ChassisConfig | None = None,
                  config_path: str | Path | None = None, data_dir: str | Path = "./data",
                  rag=None, primary_model=None, secondary_model=None, tool=None,
                  state: StateStore | None = None, approval_actions: set[str] | None = None,
                  audit=None, event_bus=None) -> ChassisRuntime:
    if config is not None and config_path is not None: raise ValueError("pass config or config_path, not both")
    cfg = config or (load_config(config_path) if config_path else ChassisConfig(version="0.4.0"))
    root = Path(data_dir); root.mkdir(parents=True, exist_ok=True)
    rag_impl = rag or SQLiteKnowledgeRag(root / "knowledge.db")
    primary = primary_model or GroundedTemplateModel()
    secondary = secondary_model or GroundedTemplateModel()
    if secondary is primary: secondary = GroundedTemplateModel()
    if getattr(secondary,"name","") == getattr(primary,"name",""):
        secondary.name = getattr(secondary, "name", "secondary") + "-secondary"
    tool_impl = tool or MockTool()
    guardrail = DefaultGuardrail(denied_actions)
    state_impl = state or SQLiteStateStore(root / "state.db")
    stop = EmergencyStop(cfg.emergency_stop)

    registry = BlockRegistry()
    registry.register(BlockDescriptor("FTH-RAG-SQLITE-001", "0.4.0", "rag", rag_impl, frozenset({"retrieve","ingest"}), "father-chassis>=0.4,<1.0"))
    registry.register(BlockDescriptor("FTH-MODEL-001", "0.4.0", "model", primary, frozenset({"generate"}), "father-chassis>=0.4,<1.0"))
    registry.register(BlockDescriptor("FTH-MODEL-002", "0.4.0", "model", secondary, frozenset({"generate"}), "father-chassis>=0.4,<1.0"))
    registry.register(BlockDescriptor("FTH-TOOL-001", "0.4.0", "tool", tool_impl, frozenset({"create_report"}), "father-chassis>=0.4,<1.0"))
    registry.register(BlockDescriptor("FTH-GUARD-001", "0.4.0", "guardrail", guardrail, frozenset({"authorize"}), "father-chassis>=0.4,<1.0"))
    registry.register(BlockDescriptor("FTH-STATE-SQLITE-001", "0.4.0", "state", state_impl, frozenset({"get","set","snapshot"}), "father-chassis>=0.4,<1.0"))

    tools = ToolRegistry()
    tools.register(ToolSpec(
        "default", tool_impl, frozenset({"create_report"}), frozenset({"agent","operator"}),
        {"create_report": ActionSchema(required=frozenset({"draft"}), allowed=frozenset({"draft"}))}
    ))
    required = set(cfg.human_approval_for) | set(approval_actions or set())

    return ChassisRuntime(
        config=cfg,
        models=ModelRouter({primary.name:primary, secondary.name:secondary}, default=primary.name, fallbacks=(secondary.name,)),
        rag=rag_impl,
        guardrail=guardrail,
        audit=audit or AuditStore(),
        metrics=Metrics(),
        event_bus=event_bus or EventBus(),
        state=state_impl,
        workflows=WorkflowEngine(),
        registry=registry,
        emergency_stop=stop,
        tools=tools,
        approval_gate=HumanApprovalGate(required),
        tracer=Tracer(),
    )
