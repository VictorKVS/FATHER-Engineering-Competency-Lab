# Architecture
Owner: Principal/Solution Architect.

ProductComposer -> ProductRegistry -> StateStore(namespace=product_registry) -> SQLite/PostgreSQL.

Responsibilities:
- ProductRegistry owns product/version identity semantics;
- StateStore owns persistence only;
- ProductComposer supplies ProductRecipe;
- ProductRuntime/Qualification consume registration.

Invariant: (product_id, version) maps to exactly one recipe_hash.

Replaceability point: StateStore.

Scaling limit: distributed locking/transactions not yet qualified.