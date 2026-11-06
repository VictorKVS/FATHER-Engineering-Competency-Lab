# AG-000 Three-Pack Run Protocol

Run each case as a clean independent Product Manager session.

## Run record
- test_pack_id
- agent_prompt_version
- rag_manifest_version
- knowledge_base_version
- runtime_model
- started_at
- completed_at

## Output
Save:
- PRODUCT_DISCOVERY_PACKAGE.yaml
- INTERVIEW_PLAN.md
- SURVEY_PLAN.md
- ECONOMIC_MODEL.yaml
- DOUBTS.md
- DECISION.md
- EVIDENCE_INDEX.yaml
- SCORECARD.yaml

## Comparison after three runs

Compare:
- Does the agent approve everything?
- Does confidence fall when evidence is weak?
- Does economic rigor change with available data?
- Does it propose cheaper validation before expensive build?
- Does it distinguish BUILD / PILOT / RESEARCH_MORE / REJECT?
- Does it avoid invented numbers?
- Does it preserve unknowns?
- Are reasons NOT to build substantive?

## Improvement
Three-run failures become:
EXPERIENCE
→ prompt patch
→ RAG/KB patch
→ regression rerun of all three packs.
