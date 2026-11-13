# Test Contract
Owner: Senior Test Architect.

Acceptance criteria:
AC-PR-01 identical recipe registration is idempotent.
AC-PR-02 conflicting recipe hash is rejected.
AC-PR-03 registration survives runtime reopen.
AC-PR-04 unknown product fails explicitly.
AC-PR-05 list ordering is deterministic.
AC-PR-06 post-restart product can execute with unchanged identity.

M2 evidence:
full regression PASS; restart restore PASS; recipe_hash stable; product execution qualified.

Performance: no qualified hard SLO yet. Any latency target is planning only until measured.

Future negative tests: malformed state, concurrent writer, migration mismatch.