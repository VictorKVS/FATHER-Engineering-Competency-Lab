# FUA-001 Flight Test 03 — Turbulence / Fault Injection

Purpose: prove fail-closed behaviour and controlled recovery under injected failures.

Profile:
- transient timeout with bounded retry;
- non-retryable security denial;
- hard model failure escapes cleanly;
- audit/evidence integrity through repeated fault events;
- existing fault/recovery stress suite;
- hostile model/policy/tool/sandbox boundary after faults;
- Docker containment regression after faults;
- final evidence audit.

PASS authorizes progression to 1.04 SECURITY COMBAT SORTIES.
