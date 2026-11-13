# G7 K5 — Entity / Relation Extraction Qualification

K5 qualifies the typed fact extraction contract over immutable K4 chunks.

Acceptance:
- Ruff/static correctness;
- full father-chassis regression;
- valid chunk set -> EXTRACTED;
- same input/policy -> same entity/relation/set hashes;
- every entity and relation has evidence chunk IDs;
- relation subject/object IDs resolve inside the emitted entity set;
- duplicate mentions deduplicate deterministically;
- unsupported text does not invent relations;
- policy version changes identity explicitly;
- malformed chunk lineage is rejected;
- confidence stays within [0,1];
- invalid extraction policy is rejected.

K5 reference rules only qualify the contract. They do not claim production-grade NLP extraction quality.
