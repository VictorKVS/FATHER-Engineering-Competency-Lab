# G7 K6 — Entity Resolution / Knowledge Graph Qualification

K6 qualifies deterministic entity resolution and evidence-backed graph construction from immutable K5 extraction sets.

Acceptance:
- Ruff/static correctness;
- full father-chassis regression;
- exact same-type/name entities merge;
- merged node preserves all entity/evidence lineage;
- same name/different type becomes explicit conflict without merge;
- relation endpoints resolve to graph nodes;
- duplicate equivalent relations deduplicate with lineage union;
- dangling relation is rejected;
- input order does not affect graph identity;
- policy version changes identity explicitly;
- no inferred edges are created;
- invalid resolution policy is rejected.

K6 v1 does not qualify probabilistic/embedding entity resolution or persistent graph databases.
