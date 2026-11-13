# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-SP-01 approved+valid provenance text parses.
AC-SP-02 HOLD/REJECTED decision blocks parse.
AC-SP-03 forged provenance/hash blocks parse.
AC-SP-04 semantically identical source content + source binding + parser version produces identical document_hash even when trace-only provenance IDs differ.
AC-SP-05 heading/paragraph order preserved.
AC-SP-06 locators preserved and deterministic.
AC-SP-07 invalid UTF-8 rejected with diagnostic.
AC-SP-08 blank input rejected/partial explicitly.
AC-SP-09 unit source hash matches source binding.
AC-SP-10 raw input bytes absent from structural evidence.
AC-SP-11 full regression PASS.

Target:
G7 K3 STRUCTURAL PARSER.