# ALINA Literary Algorithm

STORY_INPUT
→ validate explicit input
→ parse continuity anchors
→ update/read domain state
→ retrieve relevant profile knowledge
→ build explicit model context
→ invoke replaceable MODEL_SLOT
→ parse structured continuation
→ continuity validation
→ canon/proposal separation
→ evidence/provenance record
→ output continuation + state delta

## Minimal vertical slice
Phase 1 intentionally implements only:
- story input;
- continuity anchors;
- local RAG/KB;
- replaceable model slot;
- structured continuation;
- evidence.

Character/location/event graph and ledgers are added only after the vertical slice passes.
