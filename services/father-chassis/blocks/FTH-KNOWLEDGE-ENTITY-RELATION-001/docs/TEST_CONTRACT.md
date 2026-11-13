# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-ER-01 valid chunk set -> EXTRACTED.
AC-ER-02 same input/policy -> same extraction_set_hash.
AC-ER-03 every entity has evidence chunks.
AC-ER-04 every relation has evidence chunks.
AC-ER-05 dangling relation impossible/rejected.
AC-ER-06 duplicate mentions deduplicate deterministically.
AC-ER-07 unsupported text does not create invented relations.
AC-ER-08 policy version changes identity explicitly.
AC-ER-09 malformed chunk lineage rejected.
AC-ER-10 extraction confidence within [0,1].
AC-ER-11 full regression PASS.

Target:
G7 K5 ENTITY RELATION EXTRACTION.