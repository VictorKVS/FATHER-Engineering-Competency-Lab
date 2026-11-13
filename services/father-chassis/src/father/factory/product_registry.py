from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from father.factory.product_recipe import ProductRecipe


@dataclass(frozen=True, slots=True)
class ProductRegistration:
    product_id: str
    version: str
    recipe_hash: str
    status: str
    domain_pack_id: str | None
    block_ids: tuple[str, ...]


class ProductRegistry:
    """Versioned registry of factory-produced products.

    The registry fails closed on attempts to reuse the same product/version with
    a different recipe hash. Re-registering the exact same recipe is idempotent.
    """

    def __init__(self) -> None:
        self._products: dict[tuple[str, str], ProductRegistration] = {}

    def register(self, recipe: ProductRecipe, *, status: str = "ASSEMBLED") -> ProductRegistration:
        key = (recipe.product_id, recipe.version)
        candidate = ProductRegistration(
            product_id=recipe.product_id,
            version=recipe.version,
            recipe_hash=recipe.recipe_hash,
            status=status,
            domain_pack_id=recipe.domain_pack_id,
            block_ids=recipe.block_ids,
        )
        current = self._products.get(key)
        if current is not None and current.recipe_hash != candidate.recipe_hash:
            raise ValueError(
                f"product version conflict for {recipe.product_id}@{recipe.version}: "
                f"{current.recipe_hash} != {candidate.recipe_hash}"
            )
        if current is None:
            self._products[key] = candidate
        return self._products[key]

    def get(self, product_id: str, version: str) -> ProductRegistration:
        try:
            return self._products[(product_id, version)]
        except KeyError as exc:
            raise KeyError(f"unknown product: {product_id}@{version}") from exc

    def list(self) -> list[ProductRegistration]:
        return sorted(self._products.values(), key=lambda x: (x.product_id, x.version))
