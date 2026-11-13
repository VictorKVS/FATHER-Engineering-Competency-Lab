from father.bootstrap import build_runtime
from father.core.approval import HumanApprovalGate
from father.factory.block_catalog import build_reference_block_catalog
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.product_registry import ProductRegistry
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def test_product_registry_survives_runtime_reopen(tmp_path):
    first_runtime = build_runtime(data_dir=tmp_path)
    registry = ProductRegistry(store=first_runtime.state)
    requirement = CustomerRequirement(
        requirement_id="REQ-PERSIST-REGISTRY",
        title="Persistent registry product",
        needs=frozenset({"create_report"}),
    )
    recipe = ProductRecipeBuilder(
        RequirementPlanner(),
        build_reference_block_catalog(),
    ).plan(requirement, product_id="PRD-PERSIST").recipe
    assert recipe is not None
    registry.register(recipe)

    second_runtime = build_runtime(data_dir=tmp_path)
    reopened = ProductRegistry(store=second_runtime.state)
    restored = reopened.get("PRD-PERSIST", "0.1.0")

    assert restored.recipe_hash == recipe.recipe_hash


def test_approval_survives_runtime_reopen(tmp_path):
    first_runtime = build_runtime(data_dir=tmp_path)
    pending = first_runtime.approval_gate.request(
        trace_id="TRACE-PERSIST",
        action="create_report",
    )

    second_runtime = build_runtime(data_dir=tmp_path)
    restored = second_runtime.approval_gate.get(pending.approval_id)
    assert restored.status == "pending"
    assert restored.action == "create_report"

    approved = second_runtime.approval_gate.approve(restored.approval_id)

    third_runtime = build_runtime(data_dir=tmp_path)
    final = third_runtime.approval_gate.get(approved.approval_id)
    assert final.status == "approved"
