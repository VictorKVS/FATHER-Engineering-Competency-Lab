from father.bootstrap import build_runtime
from father.factory.agent_factory import AgentFactory
from father.factory.executor import FactoryExecutor
from father.factory.qualification_record import FactoryQualificationRecord
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def test_factory_execution_produces_qualification_record(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest("kb://qualification", "FATHER qualification evidence for factory execution.")

    executor = FactoryExecutor(
        runtime=runtime,
        planner=RequirementPlanner(),
        agent_factory=AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        ),
    )
    requirement = CustomerRequirement(
        requirement_id="REQ-QUAL-001",
        title="Qualification agent",
        needs=frozenset({"analyze_documents", "create_report", "enforce_policy", "run_workflow"}),
        metadata={"agent_id": "qualification-agent"},
    )

    execution = executor.execute(
        requirement=requirement,
        user_input="What qualification evidence is available?",
    )
    audit = runtime.audit.by_trace(execution.trace_id)
    record = FactoryQualificationRecord.from_execution(
        requirement_id=requirement.requirement_id,
        execution_result=execution,
        audit_events=audit,
    )

    assert record.qualified is True
    assert record.agent_id == "qualification-agent"
    assert record.trace_id == execution.trace_id
    assert record.evidence_hashes
    assert record.audit_event_count >= 2
    assert record.record_hash
    assert record.qualification_id.startswith("FQ-")
