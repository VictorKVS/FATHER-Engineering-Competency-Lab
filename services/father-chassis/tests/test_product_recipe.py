from father.factory.block_catalog import build_reference_block_catalog
from father.factory.domain_pack import DomainPack
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _builder():
    return ProductRecipeBuilder(
        RequirementPlanner(),
        build_reference_block_catalog(),
    )


def test_product_recipe_is_built_from_requirement_and_blocks():
    requirement = CustomerRequirement(
        requirement_id="REQ-PRODUCT-001",
        title="Knowledge analyst product",
        needs=frozenset({
            "analyze_documents",
            "create_report",
            "enforce_policy",
            "run_workflow",
        }),
        metadata={"agent_id": "knowledge-product-agent"},
    )

    plan = _builder().plan(requirement, product_id="PRD-KNOWLEDGE-001")

    assert plan.buildable is True
    assert plan.recipe is not None
    assert plan.recipe.product_id == "PRD-KNOWLEDGE-001"
    assert plan.recipe.agent_id == "knowledge-product-agent"
    assert plan.recipe.recipe_hash
    assert set(plan.recipe.contracts) == {
        "component",
        "data",
        "security",
        "qualification",
        "ownership_provenance",
    }


def test_product_recipe_supports_domain_pack():
    requirement = CustomerRequirement(
        requirement_id="REQ-DOMAIN-001",
        title="Security analyst",
        needs=frozenset({"analyze_documents", "create_report"}),
    )
    pack = DomainPack(
        domain_pack_id="DP-SECURITY-001",
        version="0.1.0",
        domain="cybersecurity",
        capabilities=frozenset({"policy.enforce"}),
        knowledge_sources=("SECGRAPH",),
        policies=("deny_unqualified_actions",),
    )

    plan = _builder().plan(
        requirement,
        product_id="PRD-SECURITY-001",
        domain_pack=pack,
    )

    assert plan.buildable is True
    assert plan.recipe is not None
    assert plan.recipe.domain_pack_id == "DP-SECURITY-001"
    assert "FTH-POLICY-GUARD-001" in plan.recipe.block_ids


def test_product_recipe_stops_when_need_is_unknown():
    requirement = CustomerRequirement(
        requirement_id="REQ-UNKNOWN-001",
        title="Vision product",
        needs=frozenset({"vision.analyze"}),
    )

    plan = _builder().plan(requirement, product_id="PRD-VISION-001")

    assert plan.buildable is False
    assert plan.recipe is None
    assert plan.unresolved_needs == ("vision.analyze",)
