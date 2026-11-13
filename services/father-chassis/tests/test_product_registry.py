from dataclasses import replace

import pytest

from father.factory.block_catalog import build_reference_block_catalog
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.product_registry import ProductRegistry
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _recipe():
    requirement = CustomerRequirement(
        requirement_id="REQ-REGISTRY",
        title="Registry product",
        needs=frozenset({"create_report"}),
    )
    plan = ProductRecipeBuilder(
        RequirementPlanner(),
        build_reference_block_catalog(),
    ).plan(requirement, product_id="PRD-REGISTRY")
    assert plan.recipe is not None
    return plan.recipe


def test_exact_product_registration_is_idempotent():
    registry = ProductRegistry()
    recipe = _recipe()

    first = registry.register(recipe)
    second = registry.register(recipe)

    assert first == second
    assert len(registry.list()) == 1


def test_same_product_version_with_other_recipe_hash_fails_closed():
    registry = ProductRegistry()
    recipe = _recipe()
    registry.register(recipe)

    with pytest.raises(ValueError, match="product version conflict"):
        registry.register(replace(recipe, recipe_hash="different"))
