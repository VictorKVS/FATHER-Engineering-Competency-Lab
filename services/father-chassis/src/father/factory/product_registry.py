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

    NAMESPACE = "product_registry"

    def __init__(self, store=None) -> None:
        self.store = store
        self._products: dict[tuple[str, str], ProductRegistration] = {}

    @staticmethod
    def _key(product_id: str, version: str) -> str:
        return f"{product_id}@{version}"

    def _load(self, product_id: str, version: str) -> ProductRegistration | None:
        key = (product_id, version)
        current = self._products.get(key)
        if current is not None:
            return current
        if self.store is None:
            return None
        raw = self.store.get(self.NAMESPACE, self._key(product_id, version))
        if raw is None:
            return None
        current = ProductRegistration(
            product_id=str(raw["product_id"]),
            version=str(raw["version"]),
            recipe_hash=str(raw["recipe_hash"]),
            status=str(raw["status"]),
            domain_pack_id=raw.get("domain_pack_id"),
            block_ids=tuple(raw.get("block_ids", ())),
        )
        self._products[key] = current
        return current

    def _save(self, registration: ProductRegistration) -> None:
        key = (registration.product_id, registration.version)
        self._products[key] = registration
        if self.store is not None:
            self.store.set(
                self.NAMESPACE,
                self._key(registration.product_id, registration.version),
                {
                    "product_id": registration.product_id,
                    "version": registration.version,
                    "recipe_hash": registration.recipe_hash,
                    "status": registration.status,
                    "domain_pack_id": registration.domain_pack_id,
                    "block_ids": list(registration.block_ids),
                },
            )

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
        current = self._load(recipe.product_id, recipe.version)
        if current is not None and current.recipe_hash != candidate.recipe_hash:
            raise ValueError(
                f"product version conflict for {recipe.product_id}@{recipe.version}: "
                f"{current.recipe_hash} != {candidate.recipe_hash}"
            )
        if current is None:
            self._save(candidate)
            return candidate
        return current

    def get(self, product_id: str, version: str) -> ProductRegistration:
        current = self._load(product_id, version)
        if current is None:
            raise KeyError(f"unknown product: {product_id}@{version}")
        return current

    def list(self) -> list[ProductRegistration]:
        if self.store is not None:
            for raw in self.store.snapshot(self.NAMESPACE).values():
                self._load(str(raw["product_id"]), str(raw["version"]))
        return sorted(self._products.values(), key=lambda x: (x.product_id, x.version))
