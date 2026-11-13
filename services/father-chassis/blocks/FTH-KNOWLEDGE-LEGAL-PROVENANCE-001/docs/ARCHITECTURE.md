# Architecture
Owner: Principal/Solution Architect.

SourceIntakeRecord
   ↓
SourceUsePolicyRegistry
   ↓
LegalAccessEvaluator
   ├─ deterministic rules
   ├─ evidence requirements
   └─ authority markers
   ↓
SourceAdmissibilityDecision
   +
ProvenanceRecord
   ↓
Parser Intake Gate

Boundary:
this block decides admissibility under configured policy.
It does not parse content and does not claim universal legal correctness outside that policy.