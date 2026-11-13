# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-CA-01 qualified agent meeting exact level is admitted.
AC-CA-02 agent below required level is blocked.
AC-CA-03 insufficient evidence is blocked.
AC-CA-04 missing required evidence type is blocked.
AC-CA-05 wrong domain/capability claim is blocked.
AC-CA-06 unknown agent/claim is blocked.
AC-CA-07 unknown stage policy is blocked.
AC-CA-08 admission preserves Trust qualification_id/evidence_ids/reasons.
AC-CA-09 role ownership still blocks even if competency passes.
AC-CA-10 competency pass cannot bypass KB/tool/security gates.
AC-CA-11 Trust package tests remain PASS independently.

Qualification:
full father-chassis regression + Trust tests + dedicated admission integration tests.