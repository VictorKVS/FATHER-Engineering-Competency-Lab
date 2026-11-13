# Qualification Plan
Owner: Qualification Auditor + Test Architect.

Scope: G7 M2 persistent factory lifecycle.

Entry:
static checks PASS; full regression PASS; persistent approval implementation present; current test contract.

Pass:
- pending approval survives restart;
- approved decision survives second restart;
- execution cannot bypass gate;
- matching approved action can continue and qualify.

Blockers:
lost state; action mismatch accepted; execution without required approval; regression failure.

Evidence:
artifacts/local/g7_m2_persistent_factory_lifecycle_qualification_2026-11-13.json
Canonical evidence only after verified PASS.