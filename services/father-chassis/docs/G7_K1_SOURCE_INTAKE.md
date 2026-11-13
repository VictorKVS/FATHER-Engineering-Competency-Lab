# G7 K1 — Source Intake Qualification

K1 qualifies the first Knowledge Factory production block.

Acceptance:
- Ruff/static correctness;
- full father-chassis regression;
- deterministic SHA-256 fingerprint;
- required metadata enforced;
- duplicate content detected without metadata merge;
- changed bytes under same locator produce a different hash;
- declared rights/access remain declarations, never legal approval;
- SourceIntakeRecord is immutable;
- qualification evidence contains metadata/hash references only, not raw source content.

K1 does not qualify legal rights, provenance, malware/MIME checks, parsing, chunking or indexing.
