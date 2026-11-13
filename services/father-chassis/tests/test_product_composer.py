import pytest

from father.bootstrap import build_runtime
from father.factory.agent_factory import AgentFactory
from father.factory.block_catalog import build_reference_block_catalog
from father.factory.product_composer import ProductComposer
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.product_registry import ProductRegistry
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.reference_products import osint_knowledge_spec, security_kii_spec
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _composer(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    planner = RequirementPlanner()
    return ProductComposer(
        planner=planner,
        recipe_builder=ProductRecipeBuilder(planner, build_reference_block_catalog()),
        agent_factory=AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        ),
        registry=ProductRegistry(),
    )


def test_same_factory_composes_two_distinct_products(tmp_path):
    composer = _composer(tmp_path)
    osint = osint_knowledge_spec()
    kii = security_kii_spec()

    product_a = composer.compose(
        requirement=osint.requirement,
        product_id=osint.product_id,
        product_version=osint.version,
        domain_pack=osint.domain_pack,
    )
    product_b = composer.compose(
        requirement=kii.requirement,
        product_id=kii.product_id,
        product_version=kii.version,
        domain_pack=kii.domain_pack,
    )

    assert product_a.recipe.product_id != product_b.recipe.product_id
    assert product_a.recipe.recipe_hash != product_b.recipe.recipe_hash
    assert product_a.assembly.assembly_hash != product_b.assembly.assembly_hash
    assert product_a.recipe.domain_pack_id == "DP-OSINT-001"
    assert product_b.recipe.domain_pack_id == "DP-SECURITY-KII-001"
    assert "FTH-POLICY-GUARD-001" in product_b.recipe.block_ids


def test_composer_fails_before_registration_for_unknown_need(tmp_path):
    composer = _composer(tmp_path)
    bad = CustomerRequirement(
        requirement_id="REQ-UNKNOWN",
        title="Unknown product",
        needs=frozenset({"vision.analyze"}),
    )

    with pytest.raises(ValueError, match="product recipe not buildable"):
        composer.compose(requirement=bad, product_id="PRD-UNKNOWN")
