# G7 K4 — Chunk Normalization Qualification

K4 qualifies deterministic normalized chunk production from an immutable K3 StructuralDocument.

Acceptance:
- Ruff/static correctness;
- full father-chassis regression;
- valid StructuralDocument -> CHUNKED;
- same document/policy -> same chunk hashes and chunk-set hash;
- whitespace normalization deterministic;
- source/document/unit lineage preserved;
- source locators preserved;
- no empty chunks;
- max_chars respected;
- oversize paragraph splitting deterministic;
- policy version changes identity explicitly;
- cross-document lineage mismatch rejected;
- unsupported overlap policy rejected in v1;
- no semantic rewrite/summarization is introduced.

K4 does not qualify embeddings, vector DB indexing, entity extraction or retrieval quality.
