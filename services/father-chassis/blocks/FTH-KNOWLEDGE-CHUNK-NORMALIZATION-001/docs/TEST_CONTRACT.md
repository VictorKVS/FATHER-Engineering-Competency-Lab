# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-CN-01 valid StructuralDocument -> CHUNKED.
AC-CN-02 same document/policy -> same chunk hashes/set hash.
AC-CN-03 whitespace normalization deterministic.
AC-CN-04 unit lineage preserved.
AC-CN-05 locators preserved.
AC-CN-06 no empty chunks.
AC-CN-07 max_chars respected except explicit heading-context accounting rule.
AC-CN-08 oversize paragraph splits deterministically.
AC-CN-09 cross-document lineage rejected.
AC-CN-10 policy version affects identity explicitly.
AC-CN-11 no semantic rewriting.
AC-CN-12 full regression PASS.

Target:
G7 K4 CHUNK NORMALIZATION.