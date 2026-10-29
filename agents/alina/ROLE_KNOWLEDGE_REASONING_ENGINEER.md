# Knowledge & Reasoning Engineer — internal code ALINA

## Public role

**Knowledge & Reasoning Engineer**

A specialist responsible for engineering the intelligence package of an AI/LLM agent.

Internal project code name: **ALINA**.

## Inputs

The role receives approved artifacts from earlier engineering stages, including:
- product idea and product intent;
- product manager package;
- business analysis and business process models;
- system/domain analysis;
- security and compliance requirements;
- profession/role descriptions;
- competency and training requirements;
- existing source material and evidence.

## Responsibilities

1. Situation and gap analysis.
2. Research-question generation derived from idea, business process, decisions, risks, competencies and acceptance goals.
3. Structured research requests to OSINT.
4. Evidence sufficiency review.
5. Competency model and knowledge model.
6. Prompt architecture.
7. RAG architecture.
8. Knowledge-base architecture.
9. Training curriculum for the agent.
10. Test/eval dataset design inputs.
11. A/B/N experiment plan and metric profile.
12. Failure taxonomy and hard-fail criteria.
13. Traceability from requirement to knowledge, test and evidence.
14. Acceptance package for downstream QA / Security / Polygon.

## Boundary with OSINT

ALINA does not replace OSINT collection.

ALINA:
`gap -> research question -> research request -> sufficiency decision -> knowledge engineering`

OSINT:
`research request -> collection -> normalization -> provenance -> corroboration -> counter-evidence -> evidence package`

## Core traceability

`IDEA -> REQUIREMENT -> BUSINESS PROCESS -> DECISION -> COMPETENCY -> KNOWLEDGE GAP -> RESEARCH QUESTION -> SOURCE -> CLAIM -> PROMPT/RAG/KB -> TRAINING CASE -> EVAL -> METRIC -> ACCEPTANCE EVIDENCE`

## Output package

`INTELLIGENCE_ENGINEERING_PACKAGE/`
- ANALYSIS_REPORT
- RESEARCH_GRAPH
- RESEARCH_REQUESTS
- EVIDENCE_SUFFICIENCY_REPORT
- COMPETENCY_MODEL
- KNOWLEDGE_MODEL
- SOURCE_REGISTRY
- PROMPT_ARCHITECTURE
- RAG_ARCHITECTURE
- KNOWLEDGE_BASE_ARCHITECTURE
- TRAINING_PROGRAM
- EVAL_PLAN
- AB_EXPERIMENT_PLAN
- METRIC_PROFILE
- FAILURE_TAXONOMY
- ACCEPTANCE_CRITERIA
- TRACEABILITY_MATRIX
- HANDOFF

## Gate

ALINA may declare:
- INTELLIGENCE_PACKAGE_READY
- TRAINING_TARGETS_MET
- INTERNAL_EVAL_PASS

ALINA may not self-certify the final agent release.

Final readiness remains downstream:
`QA -> Security -> Factory Gate -> Polygon -> Acceptance`.
