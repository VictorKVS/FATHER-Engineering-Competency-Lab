# EXP-ALINA-T001

## Situation
Synthetic evidence package contained a clean 100 → 100 → 70 pipeline discrepancy.

## What worked
- Explicit hypothesis rejection prevented blaming transport without evidence.
- Provenance invariant allowed equal content to be distinguished from equal observation.
- Bounded conclusion correctly stopped before engineering remediation.
- Evidence IDs made the reasoning auditable.

## Gaps discovered
1. Factory output contract lacked an explicit DecisionRecord collection.
2. Factory output contract lacked work_step_runs despite ALINA's process-engine invariant.

## Promotion
Promote these two schema gaps into the canonical ALINA factory output contract.
Do not change the analytical conclusion logic based on this test.
