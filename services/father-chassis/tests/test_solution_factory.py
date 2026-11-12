from father.bootstrap import build_runtime
from father.factory.agent_factory import AgentFactory
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner
from father.factory.solution_factory import CustomerSolutionFactory


def _factory(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    return CustomerSolutionFactory(
        RequirementPlanner(),
        AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        ),
    )


def test_customer_requirement_reaches_ready_to_build(tmp_path):
    factory = _factory(tmp_path)
    req = CustomerRequirement(
        requirement_id="REQ-READY",
        title="Knowledge analyst",
        needs=frozenset({"analyze_documents", "create_report", "enforce_policy", "run_workflow"}),
        required_permissions=frozenset({"execute:analysis", "read:evidence"}),
    )

    result = factory.plan(req)

    assert result["ready"] is True
    assert result["status"] == "READY_TO_BUILD"
    assert result["build"]["buildable"] is True
    assert result["build"]["provider_bindings"]


def test_customer_requirement_stops_on_unknown_need(tmp_path):
    factory = _factory(tmp_path)
    req = CustomerRequirement(
        requirement_id="REQ-FUTURE",
        title="Future CV analyst",
        needs=frozenset({"vision.analyze", "create_report"}),
    )

    result = factory.plan(req)

    assert result["ready"] is False
    assert result["status"] == "REQUIREMENTS_UNRESOLVED"
    assert "vision.analyze" in result["requirement"]["unresolved_needs"]
