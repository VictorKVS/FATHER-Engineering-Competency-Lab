# Three-Agent Test Strategy

Each of ALINA, OSINT and PIONEER receives three individual test packs.

Then the whole workcell receives three end-to-end packs.

## Individual packs

### ALINA
1. Clear analytical task with sufficient evidence.
2. Contradictory evidence and unresolved ambiguity.
3. Insufficient evidence requiring ResearchGap.

### OSINT
1. Straightforward multi-source research.
2. Contradictory / duplicated / dependent sources.
3. Low-coverage search with blocked sources and explicit insufficiency.

### PIONEER
1. Complete infrastructure requirements.
2. Requirements with dependency/security conflict.
3. Incomplete evidence requiring return to ALINA/OSINT.

## End-to-end packs

E2E-001:
Customer task
→ ALINA
→ OSINT
→ ALINA
→ PIONEER
→ GATE-1.

E2E-002:
Contradictory sources
→ ResearchGap loop
→ corrected architecture package.

E2E-003:
Insufficient evidence
→ architecture HOLD
→ targeted research
→ re-submit.

## Scoring dimensions
- role-boundary compliance;
- handoff schema validity;
- provenance completeness;
- evidence/claim traceability;
- contradiction handling;
- gap detection;
- rework correctness;
- architecture traceability;
- no invented facts;
- evidence quality.
