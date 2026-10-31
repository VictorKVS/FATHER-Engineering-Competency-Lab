# Algorithm

INPUT
→ validate story text
→ extract continuity anchors
→ build retrieval query
→ retrieve writing knowledge
→ assemble explicit context
→ invoke MODEL_SLOT
→ validate output contract
→ continuity checks
→ save evidence
→ return continuation

## Continuity anchors
- characters
- relationships
- locations
- chronology
- POV
- tense
- tone
- unresolved events
- explicit constraints

## Failure modes
- empty story -> HOLD
- malformed output -> RETRY once
- contradiction with explicit source fact -> FAIL
- model unavailable -> FALLBACK model slot if configured
