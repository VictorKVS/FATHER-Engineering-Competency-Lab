import pytest

from father.bootstrap import build_runtime
from father.core.access_control import ClearanceLevel, ResourceContext, SubjectContext
from father.factory.agent_factory import AgentFactory
from father.factory.executor import FactoryExecutor
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _executor(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest("kb://factory", "FATHER Factory Execution runs qualified agents on the common chassis.")
    return runtime, FactoryExecutor(
        runtime=runtime,
        planner=RequirementPlanner(),
        agent_factory=AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        ),
    )


def _requirement():
    return CustomerRequirement(
        requirement_id="REQ-EXEC-001",
        title="Knowledge analyst",
        needs=frozenset({
            "analyze_documents",
            "create_report",
            "enforce_policy",
            "run_workflow",
        }),
        required_permissions=frozenset({"execute:analysis"}),
        metadata={"agent_id": "factory-knowledge-agent"},
    )


def test_factory_builds_and_executes_agent_on_chassis(tmp_path):
    runtime, executor = _executor(tmp_path)

    result = executor.execute(
        requirement=_requirement(),
        user_input="What does FATHER Factory Execution do?",
    )

    assert result.status == "EXECUTED"
    assert result.agent_id == "factory-knowledge-agent"
    assert result.output
    assert result.evidence

    events = runtime.audit.by_trace(result.trace_id)
    received = [e for e in events if e.type == "request.received"]
    assert received
    assert received[0].payload["agent_id"] == "factory-knowledge-agent"


def test_factory_execution_respects_access_control(tmp_path):
    _, executor = _executor(tmp_path)

    subject = SubjectContext(
        subject_id="viewer",
        roles=frozenset({"viewer"}),
        clearance=ClearanceLevel.PUBLIC,
    )
    resource = ResourceContext(
        resource_id="restricted-kb",
        classification=ClearanceLevel.RESTRICTED,
    )

    with pytest.raises(PermissionError):
        executor.execute(
            requirement=_requirement(),
            user_input="Read restricted data",
            subject=subject,
            resource=resource,
            permission="execute:analysis",
        )


def test_factory_stops_before_execution_when_requirements_unresolved(tmp_path):
    runtime, executor = _executor(tmp_path)
    bad = CustomerRequirement(
        requirement_id="REQ-VISION",
        title="Future vision",
        needs=frozenset({"vision.analyze"}),
    )

    with pytest.raises(ValueError):
        executor.execute(requirement=bad, user_input="analyze image")

    assert not any(e.type == "request.received" for e in runtime.audit._events)


def test_rag_ingest_is_idempotent(tmp_path):
    runtime, _ = _executor(tmp_path)
    first = runtime.rag.ingest("kb://dedup", "same evidence")
    second = runtime.rag.ingest("kb://dedup", "same evidence")
    assert first == 1
    assert second == 0


def test_factory_enforces_manifest_human_approval_contract(tmp_path):
    from father.core.approval import ApprovalRequired

    runtime, executor = _executor(tmp_path)
    requirement = CustomerRequirement(
        requirement_id="REQ-APPROVAL-001",
        title="Controlled reporting agent",
        needs=frozenset({"analyze_documents", "create_report", "run_workflow"}),
        approval_required_for=frozenset({"create_report"}),
        metadata={"agent_id": "controlled-report-agent"},
    )

    with pytest.raises(ApprovalRequired) as exc:
        executor.execute(
            requirement=requirement,
            user_input="What does FATHER Factory Execution do?",
        )

    record = runtime.approval_gate.get(exc.value.approval_id)
    assert record.action == "create_report"
    assert record.status == "pending"
