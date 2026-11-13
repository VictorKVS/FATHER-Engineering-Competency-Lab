# Qualification Plan
Owner: Qualification Auditor + Test Architect.

Entry:
document pack approved; implementation complete; static/full regression PASS.

Pass:
- partial workflow persists;
- restart restores artifacts/history;
- identical next-stage authority after restart;
- hash tampering is rejected;
- workflow IDs isolated.

Blocking:
lost stage state; changed next stage; tamper accepted; regression failure.

Evidence:
new G7 M3 persistent engineering workflow qualification artifact.

Canonical evidence remains PENDING until actual local run.