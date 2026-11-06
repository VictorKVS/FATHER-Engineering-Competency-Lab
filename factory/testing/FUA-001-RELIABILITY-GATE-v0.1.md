# FUA-001 Reliability Gate v0.1

Purpose:
provide one target-EVM gate for deterministic reliability invariants before human acceptance.

The gate runs:
- audit hash-chain mutation tests;
- evidence full-envelope tamper tests;
- four-eyes and replay-protected approval tests;
- bounded recovery and no-retry-on-security-denial tests;
- resource-accounting invariants;
- context trust and prompt-injection exclusion tests;
- explicit compatibility PASS/FAIL/UNKNOWN tests;
- deterministic failure-injection suite;
- process-sandbox regression tests;
- Windows Job Object active-process and memory-limit EVM tests;
- final repository evidence audit.

The gate also requires:
- installation_permit remains DENIED;
- production_ready remains false.

PASS means the automated reliability gate passed on the target EVM.
It is not equivalent to mathematical 100% reliability or production certification.
HUMAN_ACCEPTANCE remains a separate gate.
