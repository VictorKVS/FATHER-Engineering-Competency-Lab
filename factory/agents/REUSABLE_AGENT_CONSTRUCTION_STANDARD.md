# Reusable Agent Construction Standard

## Principle

A verified agent is a reusable engineering template, not a one-off implementation.

New agents are created by cloning a verified agent specification and replacing only declared configurable parts.

```
VERIFIED AGENT TEMPLATE
        ↓
CLONE
        ↓
NEW ID / PUBLIC NAME / CODE NAME
        ↓
ROLE + PURPOSE + BUSINESS CONTEXT
        ↓
PROMPT / RAG / KB / TOOLS / POLICIES
        ↓
TRAINING + EVAL + A/B
        ↓
SECURITY + REGRESSION
        ↓
EVIDENCE
        ↓
NEW AGENT PASS
```

## Stable vs configurable

Stable by default:
- agent package structure;
- input/output contract mechanism;
- evidence model;
- versioning model;
- handoff model;
- test/eval framework;
- security and provenance requirements;
- naming-registry integration.

Configurable:
- stable agent ID assigned for the new agent;
- public name and internal code name;
- role and purpose;
- business/domain context;
- Prompt;
- RAG policy;
- Knowledge Base;
- tool bindings;
- model policy;
- competency model;
- training program;
- test/eval datasets;
- metric thresholds;
- acceptance criteria.

## Clone gate

Cloning does not create a ready agent.

State machine:

`TEMPLATE_VERIFIED -> CLONED_DRAFT -> CONFIGURED -> INTELLIGENCE_READY -> TESTING -> EVIDENCE_READY -> PASS -> RELEASE_CANDIDATE`

Any hard-fail returns the agent to CONFIGURED or INTELLIGENCE_READY depending on failure origin.

## Naming

Every clone receives immutable stable IDs. Public names are resolved through the Naming Registry and may later change without breaking contracts.

## Inheritance

The clone manifest records:
- template_agent_id;
- template_version;
- template_commit;
- inherited components;
- overridden components;
- new stable IDs;
- test suite version;
- evidence references.

## Prohibition

Do not copy an agent folder and manually rename arbitrary strings. That destroys provenance and makes regression unreliable.
