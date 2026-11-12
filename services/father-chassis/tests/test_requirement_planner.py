from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def test_requirement_planner_builds_manifest_from_customer_needs():
    planner = RequirementPlanner()
    req = CustomerRequirement(
        requirement_id="REQ-001",
        title="Document compliance analyst",
        needs=frozenset({
            "analyze_documents",
            "create_report",
            "enforce_policy",
            "trace_decisions",
            "run_workflow",
        }),
        required_permissions=frozenset({"execute:analysis", "read:evidence"}),
        approval_required_for=frozenset({"create_report"}),
        metadata={
            "agent_id": "compliance-analyst",
            "max_steps": "8",
            "timeout_seconds": "90",
            "max_cost_usd": "0.25",
        },
    )

    plan = planner.plan(req)

    assert plan.complete is True
    assert plan.agent_manifest.agent_id == "compliance-analyst"
    assert "knowledge.retrieve" in plan.agent_manifest.capabilities
    assert "model.generate" in plan.agent_manifest.capabilities
    assert "decision.trace" in plan.agent_manifest.capabilities
    assert plan.agent_manifest.max_steps == 8


def test_requirement_planner_preserves_unresolved_need():
    planner = RequirementPlanner()
    req = CustomerRequirement(
        requirement_id="REQ-002",
        title="Future vision agent",
        needs=frozenset({"vision.analyze", "create_report"}),
    )

    plan = planner.plan(req)

    assert plan.complete is False
    assert plan.unresolved_needs == ("vision.analyze",)
