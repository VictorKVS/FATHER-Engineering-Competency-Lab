# Temporary LLM Runtime — GPT as FATHER Agent Executor

## Purpose

Until local LLMs are connected to FATHER, ChatGPT may temporarily execute the role of a registered specialist agent.

This is an execution substitution, not a change of agent identity.

## Execution rule

For any task assigned to a FATHER agent:

1. Load Agent Registry entry.
2. Load canonical ROLE/PROMPT.
3. Load ALGORITHM.
4. Load RAG_MANIFEST.
5. Retrieve only relevant approved knowledge sources.
6. Load INPUT_CONTRACT.
7. Execute the task step by step according to the agent process.
8. Produce OUTPUT_CONTRACT.
9. Run EVALS / CHECKLIST.
10. Save evidence, gaps and lessons learned.
11. Propose updates to Prompt/RAG/KB only from observed task evidence.
12. Commit approved improvements to GitHub.

## Learning rule

The temporary runtime does not claim that the underlying model has been retrained.

FATHER learning occurs through versioned artifacts:
- prompt improvements;
- RAG collection improvements;
- knowledge-base additions;
- algorithms/runbooks;
- eval datasets;
- test cases;
- accepted/rejected experience.

These artifacts become training/distillation material for future local models.

## Improvement loop

TASK
→ RUN
→ RESULT
→ EVAL
→ ERROR/GAP
→ EXPERIENCE
→ PROMPT/RAG/KB PATCH
→ REGRESSION TEST
→ PROMOTE

## Hard constraints

- Do not invent missing authoritative sources.
- Do not silently rewrite canonical knowledge.
- Preserve provenance.
- Domain decisions stay with the domain owner.
- Security-sensitive and destructive actions require the appropriate approval gate.
- Failed experiments remain in Experience Store.
