from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from father.factory.agent_factory import AgentFactory
from father.factory.block_catalog import build_reference_block_catalog
from father.factory.executor import FactoryExecutionResult, FactoryExecutor
from father.factory.product_composer import ComposedProduct, ProductComposer
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.product_registry import ProductRegistry
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.reference_products import ReferenceProductSpec
from father.factory.requirement_planner import RequirementPlanner


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class ProductRunRecord:
    product_id: str
    version: str
    recipe_hash: str
    assembly_hash: str
    trace_id: str
    workflow_id: str
    qualification_id: str
    qualification_hash: str
    qualified: bool
    evidence_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AssembledProductRuntime:
    """Reference vertical from product specification to qualified chassis execution."""

    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.planner = RequirementPlanner()
        self.agent_factory = AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        )
        self.registry = ProductRegistry(store=runtime.state)
        self.composer = ProductComposer(
            planner=self.planner,
            recipe_builder=ProductRecipeBuilder(
                self.planner,
                build_reference_block_catalog(),
            ),
            agent_factory=self.agent_factory,
            registry=self.registry,
        )
        self.executor = FactoryExecutor(
            runtime=runtime,
            planner=self.planner,
            agent_factory=self.agent_factory,
        )

    def compose(self, spec: ReferenceProductSpec) -> ComposedProduct:
        return self.composer.compose(
            requirement=spec.requirement,
            product_id=spec.product_id,
            product_version=spec.version,
            domain_pack=spec.domain_pack,
        )

    def execute(
        self,
        *,
        spec: ReferenceProductSpec,
        user_input: str,
        approval_id: str | None = None,
    ) -> tuple[ComposedProduct, FactoryExecutionResult, ProductRunRecord]:
        product = self.compose(spec)
        execution = self.executor.execute(
            requirement=spec.requirement,
            user_input=user_input,
            approval_id=approval_id,
        )
        qualification = execution.qualification
        payload = {
            "product_id": product.recipe.product_id,
            "version": product.recipe.version,
            "recipe_hash": product.recipe.recipe_hash,
            "assembly_hash": product.assembly.assembly_hash,
            "trace_id": execution.trace_id,
            "workflow_id": execution.workflow_id,
            "qualification_id": str(qualification["qualification_id"]),
            "qualification_hash": str(qualification["record_hash"]),
            "qualified": bool(qualification["qualified"]),
        }
        evidence_hash = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        record = ProductRunRecord(**payload, evidence_hash=evidence_hash)
        return product, execution, record
