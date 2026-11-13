# Data and State
Owner: System Analyst + Data Architect.

Entity: ProductRegistration.

Persisted fields:
product_id, version, recipe_hash, status, domain_pack_id, block_ids.

Consistency invariant:
(product_id, version) -> one recipe_hash.

Durability:
StateStore is durable source across restart; local cache is acceleration only.

Retention: until lifecycle policy defines removal/supersession.
Migration: schema versioning must be designed before persisted field changes.
Concurrency: multi-writer semantics not yet qualified.