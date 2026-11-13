from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from father.factory.agent_factory import AgentBuildPlan, AgentFactory
from father.factory.domain_pack import DomainPack
from father.factory.product_recipe import ProductRecipe, ProductRecipeBuilder
from father.factory.product_registry import ProductRegistration, ProductRegistry
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class ProductAssemblyRecord:
    assembly_id: str
    product_id: str
    version: str
    requirement_id: str
    recipe_hash: str
    agent_id: str
    block_ids: tuple[str, ...]
    provider_bindings: tuple[dict[str, Any], ...]
    contracts: tuple[str, ...]
    required_evidence: tuple[str, ...]
    assembly_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ComposedProduct:
    recipe: ProductRecipe
    agent_build: AgentBuildPlan
    registration: ProductRegistration
    assembly: ProductAssemblyRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe": self.recipe.to_dict(),
            "agent_build": self.agent_build.to_dict(),
            "registration": asdict(self.registration),
            "assembly": self.assembly.to_dict(),
        }


class ProductComposer:
    """Composes a registered product from requirement, blocks and agent contracts."""

    def __init__(
        self,
        *,
        planner: RequirementPlanner,
        recipe_builder: ProductRecipeBuilder,
        agent_factory: AgentFactory,
        registry: ProductRegistry,
    ) -> None:
        self.planner = planner
        self.recipe_builder = recipe_builder
        self.agent_factory = agent_factory
        self.registry = registry

    def compose(
        self,
        *,
        requirement: CustomerRequirement,
        product_id: str,
        product_version: str = "0.1.0",
        domain_pack: DomainPack | None = None,
    ) -> ComposedProduct:
        recipe_plan = self.recipe_builder.plan(
            requirement,
            product_id=product_id,
            product_version=product_version,
            domain_pack=domain_pack,
        )
        if not recipe_plan.buildable or recipe_plan.recipe is None:
            unresolved = list(recipe_plan.unresolved_needs) + list(
                recipe_plan.block_match.unresolved_capabilities
            )
            raise ValueError("product recipe not buildable: " + ",".join(sorted(set(unresolved))))

        requirement_plan = self.planner.plan(requirement)
        agent_build = self.agent_factory.plan(requirement_plan.agent_manifest)
        if not agent_build.buildable:
            raise ValueError("agent build failed: " + "; ".join(agent_build.errors))

        recipe = recipe_plan.recipe
        registration = self.registry.register(recipe)

        payload = {
            "product_id": recipe.product_id,
            "version": recipe.version,
            "requirement_id": recipe.requirement_id,
            "recipe_hash": recipe.recipe_hash,
            "agent_id": agent_build.agent_id,
            "block_ids": recipe.block_ids,
            "provider_bindings": tuple(x.__dict__ if hasattr(x, "__dict__") else {
                "capability": x.capability,
                "provider_id": x.provider_id,
                "provider_kind": x.provider_kind,
                "provider_version": x.provider_version,
            } for x in agent_build.provider_bindings),
            "contracts": recipe.contracts,
            "required_evidence": recipe.required_evidence,
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        assembly = ProductAssemblyRecord(
            assembly_id=f"ASM-{digest[:16]}",
            assembly_hash=digest,
            **payload,
        )
        return ComposedProduct(
            recipe=recipe,
            agent_build=agent_build,
            registration=registration,
            assembly=assembly,
        )
