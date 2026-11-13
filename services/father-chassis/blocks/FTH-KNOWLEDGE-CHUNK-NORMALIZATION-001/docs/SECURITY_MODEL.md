# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- hidden semantic rewrite during normalization;
- lineage loss;
- cross-document contamination;
- chunk policy drift;
- oversized input resource abuse;
- prompt injection affecting chunk boundaries.

Controls:
- deterministic non-LLM algorithm;
- explicit policy id/version;
- exact structural lineage;
- no cross-document merge;
- bounded max_chars;
- validation of unit/document binding;
- canonical hashes.

Future:
tokenizer-specific limits and signed chunk-policy releases.