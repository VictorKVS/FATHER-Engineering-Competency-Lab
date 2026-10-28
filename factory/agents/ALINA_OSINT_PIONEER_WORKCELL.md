# FATHER Workcell — ALINA + OSINT + PIONEER

## Purpose

Build one practical three-specialist workcell for real FATHER tasks.

## Roles

### AG-001 ALINA
Owns:
- task decomposition;
- research questions;
- hypotheses;
- analytical claims;
- contradictions review;
- conclusions;
- knowledge normalization;
- process/evidence traceability.

Does NOT own:
- collection transport;
- raw-source acquisition decisions;
- infrastructure architecture execution.

### AG-010 OSINT_EXPERT
Owns:
- search strategy;
- source classes;
- methods/tools;
- collection;
- RAW preservation;
- provenance;
- normalization/deduplication;
- corroboration/independence observations;
- contradiction delivery;
- coverage/sufficiency;
- EvidencePackage.

Does NOT own:
- final analytical conclusions.

### AG-005 PIONEER
Owns:
- infrastructure architecture;
- topology;
- dependency graph;
- addressing/network plan;
- bill of materials;
- infrastructure threat-model input;
- acceptance test plan;
- GATE-1 handoff to TIMA.

Does NOT:
- deploy infrastructure;
- consume cloud credentials;
- silently modify approved requirements.

## Canonical loop

PROJECT / CUSTOMER
→ ALINA creates ResearchRequest
→ OSINT creates SearchPlanProposal
→ ALINA ACCEPT / AMEND / REJECT
→ OSINT Collection / Processing
→ EvidencePackage
→ ALINA AnalyticalAssessment
→ ResearchGap OR bounded Conclusion
→ if infrastructure/system implications exist
→ PIONEER receives Requirements + Evidence + Constraints
→ Architecture / Topology / BOM / Test Plan
→ GATE-1
→ TIMA

## Backward loops

PIONEER may return:
- missing technical requirement;
- unresolved dependency;
- missing evidence;
- infeasible constraint.

Then:
PIONEER
→ ALINA
→ ResearchGap
→ OSINT
→ new EvidencePackage
→ ALINA
→ PIONEER

## Audit invariant

Every important technical decision must trace:

Architecture Decision
→ Requirement / Constraint
→ Analytical Claim
→ Evidence
→ Material
→ RAW
→ Collection
→ SearchPlan
→ ResearchRequest.

## First workcell objective

Use this three-agent chain as one of the first real FATHER regression tracks.

We test not only the final output, but:
- handoff quality;
- missing-context detection;
- provenance;
- role-boundary compliance;
- rework loop;
- evidence-driven architecture.
