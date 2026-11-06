# FATHER 000–100 — Stage-by-Stage Engineering Standard

## Principle

FATHER is debugged sequentially from Stage 000 through Stage 100.

A later stage must not be considered verified while an earlier required stage is unresolved.

Each stage is a reproducible engineering unit with its own:
- purpose;
- owner;
- ROLE / PROMPT / ALGORITHM;
- RAG / KB;
- input/output contracts;
- reference run;
- local-LLM emulation run;
- local-LLM real run;
- metrics;
- A/B comparison;
- evidence;
- gate.

## Four proof layers

### P1 — Reference Agent Run
Reference Agent Runtime temporarily executes the agent according to the stage Prompt/RAG/KB.

Purpose:
- validate instructions;
- expose ambiguity;
- identify missing knowledge;
- produce reference output;
- improve Prompt/RAG/KB.

Every change must be explained and versioned.

### P2 — Local LLM Emulation
Run the same stage as if a local model were executing it:
- strict context package;
- explicit prompt;
- bounded knowledge;
- exact input/output schema;
- no hidden conversational context.

Purpose:
prove that the stage does not depend on Reference Agent Runtime-specific implicit context.

### P3 — Local LLM Runtime
Execute on the actual local model.

Capture:
- model identity/version;
- prompt version;
- RAG version;
- KB version;
- parameters;
- hardware/runtime;
- latency;
- tokens/context;
- output;
- failures.

### P4 — Acceptance / A-B
Compare Reference vs Local.

Measure:
- contract validity;
- factual/evidence quality;
- completeness;
- traceability;
- hallucination/invention rate;
- decision quality;
- latency;
- resource use;
- cost;
- reproducibility.

If below threshold:
Prompt/RAG/KB/parameters/model selection are changed and the stage is rerun.

## Promotion

DRAFT
→ REFERENCE_VERIFIED
→ EMULATION_VERIFIED
→ LOCAL_LLM_VERIFIED
→ AB_ACCEPTED
→ STAGE_PASS

No stage may receive STAGE_PASS without evidence from the required layers.
