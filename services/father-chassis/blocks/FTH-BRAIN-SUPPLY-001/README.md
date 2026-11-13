# FTH-BRAIN-SUPPLY-001 — Brain Supply Resolver

Determines which qualified Brain Package may be supplied to a specific FATHER agent/task context.

## Status

**B6 document pack + implementation candidate; qualification pending local Windows run.**

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

## Qualification target

A local qualification harness must prove matching, denial, ambiguity, deterministic identity and full chassis regression before this block may be promoted.
