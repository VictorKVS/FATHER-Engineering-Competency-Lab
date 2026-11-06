# AG-STORY-001

Minimal FATHER agent used to prove the progressive factory pattern.

Composition:
`Story Input + Prompt + Local RAG + Knowledge Base + Replaceable Model Slot + Output Contract + Eval + Evidence`

First goal:
prove one complete agent cell before adding more agents.

Later growth:
- richer story graph;
- character memory;
- semantic retrieval;
- multiple writing modes;
- model A/B/N;
- editor/reviewer second agent.


## Migration status

This package is now TEMPORARY.

Canonical identity:
`AG-001 ALINA / profile=LITERARY / capability=STORY_CONTINUATION`

Rules:
- do not add new domain features here;
- only bug fixes required to keep the vertical slice runnable are allowed;
- all new literary requirements, domain concepts, prompts, RAG/KB and evals belong under `agents/alina/profiles/literary/`;
- runtime code from this package must be absorbed into the ALINA Literary profile after the first working single-model proof.
