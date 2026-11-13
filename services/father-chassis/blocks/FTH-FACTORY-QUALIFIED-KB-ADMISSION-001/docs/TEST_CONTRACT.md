# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-KB-01 qualified release for every required KB -> ADMIT.
AC-KB-02 missing required release -> BLOCK.
AC-KB-03 status != QUALIFIED -> BLOCK.
AC-KB-04 empty provenance/source hashes -> BLOCK.
AC-KB-05 missing retrieval evidence -> BLOCK.
AC-KB-06 wrong kb_id mapping -> BLOCK.
AC-KB-07 admitted decision preserves release IDs/hashes/evidence refs.
AC-KB-08 workflow strict KB mode without gate -> fail closed.
AC-KB-09 competency PASS cannot bypass KB FAIL.
AC-KB-10 role/competency/KB traces coexist in StageResult.
AC-KB-11 persistence/restart preserves KB admission trace.
AC-KB-12 full regression remains PASS.

Target qualification:
G7 M6 QUALIFIED KB ADMISSION.