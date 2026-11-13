from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from father.factory.block_catalog import BlockCatalog, BlockMatchResult
from father.factory.domain_pack import DomainPack
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class ProductRecipe:
    product_id: str
    version: str
    requirement_id: str
    agent_id: str
    block_ids: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    domain_pack_id: str | None
    contracts: tuple[str, ...]
    required_evidence: tuple[str, ...]
    recipe_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProductRecipePlan:
    recipe: ProductRecipe | None
    block_match: BlockMatchResult
    unresolved_needs: tuple[str, ...]

    @property
    def buildable(self) -> bool:
        return self.recipe is not None and self.block_match.complete and not self.unresolved_needs


class ProductRecipeBuilder:
    """Transforms customer requirements into a deterministic product composition recipe."""

    def __init__(self, planner: RequirementPlanner, catalog: BlockCatalog) -> None:
        self.planner = planner
        self.catalog = catalog

    def plan(
        self,
        requirement: CustomerRequirement,
        *,
        product_id: str,
        product_version: str = "0.1.0",
        domain_pack: DomainPack | None = None,
    ) -> ProductRecipePlan:
        req_plan = self.planner.plan(requirement)
        required_capabilities = set(req_plan.agent_manifest.capabilities)

        if domain_pack is not None:
            errors = domain_pack.validate()
            if errors:
                raise ValueError("invalid domain pack: " + "; ".join(errors))
            required_capabilities.update(domain_pack.capabilities)

        block_match = self.catalog.match(required_capabilities)
        if req_plan.unresolved_needs or not block_match.complete:
            return ProductRecipePlan(
                recipe=None,
                block_match=block_match,
                unresolved_needs=req_plan.unresolved_needs,
            )

        payload = {
            "product_id": product_id,
            "version": product_version,
            "requirement_id": requirement.requirement_id,
            "agent_id": req_plan.agent_manifest.agent_id,
            "block_ids": tuple(b.block_id for b in block_match.selected_blocks),
            "required_capabilities": tuple(sorted(required_capabilities)),
            "domain_pack_id": domain_pack.domain_pack_id if domain_pack else None,
            "contracts": (
                "component",
                "data",
                "security",
                "qualification",
                "ownership_provenance",
            ),
            "required_evidence": (
                "unit_tests",
                "integration_tests",
                "security_checks",
                "runtime_trace",
                "qualification_record",
            ),
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        recipe = ProductRecipe(
            **payload,
            recipe_hash=digest,
        )
        return ProductRecipePlan(
            recipe=recipe,
            block_match=block_match,
            unresolved_needs=(),
        )
