# FATHER Model Assembly Canon

## Principle

FATHER does not bind an agent to one LLM.

An executable specialist is assembled from versioned layers:

AGENT IDENTITY
+ ROLE
+ PROMPT
+ ALGORITHM
+ RAG
+ KNOWLEDGE BASE
+ TOOLS
+ POLICIES
+ INPUT/OUTPUT CONTRACTS
+ METRICS
+ EVALS
+ EXPERIENCE
+ MODEL SLOT
= EXECUTABLE AGENT CONFIGURATION

The LLM is a replaceable inference engine.

## Canonical sources

Assembly must reuse existing verified FATHER assets before creating new ones:
- ALINA analytical/process contracts;
- OSINT evidence/provenance protocols;
- PIONEER engineering/gate contracts;
- FATHER_CODEX programming rules;
- TIMA DevOps/DevSecOps/runtime rules;
- Security Specialist / SecGraph / regulatory knowledge;
- Test Engineer rationale and verification contracts;
- Polygon independent RC verification.

## Assembly sequence

1. Resolve agent.
2. Resolve stage.
3. Resolve exact prompt version.
4. Resolve RAG manifest.
5. Resolve KB version.
6. Resolve tools and permissions.
7. Resolve security policy.
8. Resolve output schema.
9. Resolve metrics and eval suite.
10. Insert model into MODEL_SLOT.
11. Execute.
12. Validate.
13. Score.
14. Compare against reference/challenger.
15. Save evidence.
16. Promote or reject configuration.

## Configuration identity

A configuration is immutable and identified by:

agent_id
+ stage_id
+ model_id
+ quantization
+ prompt_version
+ rag_version
+ kb_version
+ toolset_version
+ policy_version
+ eval_version
+ parameter_profile

Changing any element creates a new candidate configuration.

## Promotion

CANDIDATE
→ CONTRACT PASS
→ FUNCTIONAL PASS
→ SECURITY PASS
→ EVAL PASS
→ A/B ACCEPTED
→ REGRESSION PASS
→ PROMOTED

A promoted configuration becomes Best Known Configuration for that agent/stage, not a permanent model lock-in.
