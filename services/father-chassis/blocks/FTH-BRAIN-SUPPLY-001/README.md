# FTH-BRAIN-SUPPLY-001 — Brain Supply Resolver

Determines which qualified Brain Package may be supplied to a specific FATHER agent/task context.

## Status

**QUALIFIED by local Windows G7 Brain Supply run; canonical evidence recorded.**

## Why this block exists

Agents must not choose databases or brains directly. Supply must be policy-driven, deterministic and fail-closed.

## Contract

```text
AgentBrainRequest
+ Candidate Brain Packages
+ BrainSupplyPolicy
        ↓
BrainSupplyResolver
        ↓
BrainSupplyDecision
```

## Primary rules

- exact Brain Class in reference v1;
- all requested capabilities required;
- role/domain/supply-mode restrictions enforced;
- tenant boundary enforced;
- classification authorization enforced;
- only qualified/released packages eligible;
- revoked packages blocked;
- no silent fallback;
- deterministic decision identity.

## Qualification

Local Windows qualification: **PASS**

- Ruff: PASS
- full chassis regression: **188 passed**
- Agent Class A* / Brain Class B* separation: PASS
- fail-closed matching and security negatives: PASS
- deterministic identity: PASS

Canonical evidence:
`artifacts/canonical/QUALIFICATION_EVIDENCE.json`
