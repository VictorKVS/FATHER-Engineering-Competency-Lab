# G7 K3 — Structural Parser Qualification

K3 qualifies deterministic structural extraction from an APPROVED, provenance-bound source.

Acceptance:
- Ruff/static correctness;
- full father-chassis regression;
- approved source parses;
- same input/parser version -> same document_hash;
- heading/paragraph order preserved;
- locators deterministic;
- HOLD decision rejected;
- forged provenance rejected;
- content hash mismatch rejected;
- invalid UTF-8 rejected;
- unsupported media type rejected;
- every structural unit preserves source_id/source_hash;
- canonical qualification evidence contains metadata/hashes only, not raw source bytes.

K3 v1 qualifies only text/plain and text/markdown reference parsing.
