from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .registry import BlockRegistry


@dataclass(frozen=True, slots=True)
class ProductPack:
    product_id: str
    chassis: str
    required_capabilities: frozenset[str]
    domain: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BomItem:
    block_id: str
    version: str
    kind: str
    disposition: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FactoryBOM:
    product_id: str
    chassis: str
    items: tuple[BomItem, ...]
    missing_capabilities: tuple[str, ...]

    @property
    def buildable(self) -> bool:
        return not self.missing_capabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "chassis": self.chassis,
            "buildable": self.buildable,
            "missing_capabilities": list(self.missing_capabilities),
            "items": [asdict(i) for i in self.items],
        }


class FactoryPlanner:
    def __init__(self, registry: BlockRegistry) -> None:
        self.registry = registry

    def build_bom(self, pack: ProductPack) -> FactoryBOM:
        blocks = self.registry.list()
        provided: set[str] = set()
        items: list[BomItem] = []
        for block in blocks:
            relevant = bool(pack.required_capabilities & block.capabilities)
            if not relevant:
                continue
            provided.update(block.capabilities)
            items.append(BomItem(
                block_id=block.block_id,
                version=block.version,
                kind=block.kind,
                disposition="REUSE",
                capabilities=tuple(sorted(block.capabilities)),
            ))
        missing = tuple(sorted(pack.required_capabilities - provided))
        return FactoryBOM(pack.product_id, pack.chassis, tuple(items), missing)


OSINT_KNOWLEDGE_PACK = ProductPack(
    product_id="FTH-PRODUCT-OSINT-KNOWLEDGE-001",
    chassis="C2_KNOWLEDGE_RAG",
    domain="osint",
    required_capabilities=frozenset({
        "retrieve", "ingest", "generate", "create_report", "get", "set", "authorize"
    }),
    metadata={"stage": "reference-product-pack"},
)
