# Interfaces and Variables
Owner: Architect + System Analyst.

register(recipe, status="ASSEMBLED") -> ProductRegistration

Inputs:
- recipe.product_id: str, required, non-null;
- recipe.version: str, required, non-null;
- recipe.recipe_hash: str, required, non-null;
- recipe.domain_pack_id: str|null;
- recipe.block_ids: tuple[str,...];
- status: str, default ASSEMBLED.

Output fields:
product_id, version, recipe_hash, status, domain_pack_id, block_ids.

get(product_id: str, version: str) -> ProductRegistration.
list() -> list[ProductRegistration], sorted by product_id/version.

Persistence:
namespace=product_registry
key=<product_id>@<version>

Errors:
- ValueError on recipe hash conflict;
- KeyError on unknown product.

No developer may introduce undeclared cross-block variables.