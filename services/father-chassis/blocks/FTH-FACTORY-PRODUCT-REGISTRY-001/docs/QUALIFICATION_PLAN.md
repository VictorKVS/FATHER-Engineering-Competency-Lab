# Qualification Plan
Owner: Qualification Auditor + Test Architect.

Scope: G7 M2 persistent factory lifecycle.

Entry:
static checks PASS; regression PASS; current persistence implementation; current test contract.

Pass:
- registration survives restart;
- recipe_hash unchanged;
- conflict remains fail-closed;
- post-restart execution qualifies.

Blockers:
lost registration; hash mismatch; silent overwrite; regression failure.

Local evidence:
artifacts/local/g7_m2_persistent_factory_lifecycle_qualification_2026-11-13.json

Canonical evidence promoted only after verified PASS.