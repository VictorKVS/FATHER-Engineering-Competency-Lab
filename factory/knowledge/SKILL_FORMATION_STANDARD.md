# Skill Formation Standard

Knowledge is not treated as a skill until the agent demonstrates correct use under test.

## Canonical chain

`KNOWLEDGE -> EXAMPLE -> PROCEDURE -> PRACTICE -> DECISION -> FEEDBACK -> EVAL -> REINFORCEMENT -> COMPETENCY EVIDENCE`

## Skill record

Each skill must define:
- skill_id;
- competency_id;
- required knowledge nodes;
- prerequisite skills;
- procedures;
- tool usage;
- normal cases;
- edge cases;
- adversarial cases when relevant;
- expected decisions;
- forbidden decisions;
- scoring rubric;
- hard-fail conditions;
- training cases;
- evaluation cases;
- pass threshold;
- regression cases;
- evidence references.

## Learning loop

1. Present grounded knowledge.
2. Show worked examples.
3. Require application through procedures/cases.
4. Capture the decision and rationale.
5. Classify the error.
6. Apply remediation targeted at the failure.
7. Re-run unseen evaluation.
8. Add regression case.
9. Promote only after repeated evidence.

## Important boundary

Adding a document to RAG or KB is not skill acquisition.
Skill acquisition requires behavioral evidence on tasks.
