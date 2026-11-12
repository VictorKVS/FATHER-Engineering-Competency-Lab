from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class ProductComponent:
    capability: str
    source: str
    block_id: str | None = None
    notes: str = ""

@dataclass
class ReuseReport:
    product_id: str
    components: list[ProductComponent]

    @property
    def shared(self) -> list[ProductComponent]:
        return [c for c in self.components if c.source == "SHARED"]

    @property
    def adapted(self) -> list[ProductComponent]:
        return [c for c in self.components if c.source == "ADAPT"]

    @property
    def new(self) -> list[ProductComponent]:
        return [c for c in self.components if c.source == "NEW"]

    @property
    def reuse_ratio(self) -> float:
        total = len(self.components)
        return 0.0 if total == 0 else len(self.shared) / total

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "counts": {
                "shared": len(self.shared),
                "adapted": len(self.adapted),
                "new": len(self.new),
                "total": len(self.components),
            },
            "reuse_ratio": round(self.reuse_ratio, 4),
            "components": [asdict(c) for c in self.components],
        }

def compare_capabilities(
    product_id: str,
    required: Iterable[str],
    shared: dict[str, str],
    adaptable: dict[str, str] | None = None,
) -> ReuseReport:
    adaptable = adaptable or {}
    items: list[ProductComponent] = []
    for cap in required:
        if cap in shared:
            items.append(ProductComponent(cap, "SHARED", shared[cap]))
        elif cap in adaptable:
            items.append(ProductComponent(cap, "ADAPT", adaptable[cap]))
        else:
            items.append(ProductComponent(cap, "NEW", None))
    return ReuseReport(product_id, items)
