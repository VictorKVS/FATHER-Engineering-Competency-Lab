# FATHER Brain & Knowledge Infrastructure
## 03 — Architecture

**Stage:** Architecture  
**Status:** ARCHITECTURE BASELINE / FIRST IMPLEMENTATION SLICE  
**Decision:** first implementation slice is **Brain Supply Resolver**, not a database adapter.

## 1. Architectural intent

FATHER separates five concerns:

1. **Brain design** — what knowledge capabilities an agent needs.
2. **Brain production** — how knowledge is ingested, normalized, resolved and packaged.
3. **Brain storage** — where representations physically live.
4. **Brain supply** — which agent may receive which Brain Package, when and under what scope.
5. **Brain qualification** — whether the package and its bindings are proven fit for use.

The first implementation slice is Brain Supply because storage selection is meaningless until FATHER knows what it is supplying, to whom, and under which authority.

## 2. Two independent class axes

FATHER must never collapse Agent Class and Brain Class into one scale.

```text
AGENT CLASS                     BRAIN CLASS

A1 Simple                       B1 Embedded
A2 Standard                     B2 RAG
A3 Analyst                      B3 Analytical
A4 Enterprise                   B4 Enterprise
A5 Security / High-control      B5 High Assurance
A6 Distributed / Complex        B6 Massive
```

These are **independent axes**, not fixed pairs.

Examples:

```text
A2 + B5   valid when a simple agent requires a highly assured brain
A5 + B2   valid when a security-controlled agent needs a small RAG brain
A3 + B3   common but not mandatory
```

Every Brain Package explicitly declares `compatible_agent_classes`.
Every request explicitly declares `requested_brain_class`.

## 3. Agent supply model

An agent does not connect directly to a database.

```text
Agent / Task
   ↓
BrainSupplyRequest
   ├─ agent_class A*
   ├─ requested_brain_class B*
   ├─ role
   ├─ domains
   ├─ required capabilities
   ├─ supply mode
   ├─ tenant
   └─ security clearance
   ↓
Brain Supply Resolver
   ↓
AUTHORIZED BrainBinding
   ↓
Retrieval / Knowledge Access Boundary
   ↓
Storage adapters
```

## 4. Supply modes

- **BASELINE** — stable brain attached to an agent profile.
- **ROLE_SCOPED** — brain added for the active role.
- **DOMAIN_SCOPED** — brain added for a knowledge domain.
- **TASK_SCOPED** — temporary brain for a task/workflow.
- **SESSION_SCOPED** — temporary brain for a controlled session.
- **INCIDENT_SCOPED** — security/operations brain bound to an incident.

A Brain Package explicitly declares supported supply modes.

## 5. Matching dimensions

No package is eligible unless all mandatory dimensions pass:

| Dimension | Rule |
|---|---|
| Release state | package must be QUALIFIED or RELEASED according to policy |
| Brain class | package B-class must match requested B-class in reference v1 |
| Agent class | requester A-class must be declared compatible |
| Role | request role must be allowed where restricted |
| Domain | requested domains must be covered |
| Capability | all required capabilities must be present |
| Supply mode | requested mode must be supported |
| Classification | agent must be authorized for package classification |
| Tenant | package must be global or match tenant |
| Revocation | revoked/superseded package must not be selected |

## 6. Fail-closed decisions

The resolver returns one of:

- `BOUND`
- `NO_MATCH`
- `AMBIGUOUS`
- `REJECTED`

It never silently substitutes a “close enough” brain.

## 7. Minimal sufficient selection

Within the requested Brain Class:

1. exact tenant is preferred over global;
2. fewer unnecessary capabilities are preferred;
3. unresolved equal candidates produce `AMBIGUOUS`.

No larger Brain Class is selected merely because it has more capabilities.

## 8. Brain Class is not clearance

B1…B6 express knowledge-system complexity/assurance profile.
Security classification and authorization are separate properties.

A B2 brain may contain protected information.
A B5 designation never grants permission to read information.

## 9. Storage boundary

Brain Supply Resolver knows capabilities and package identity, not PostgreSQL/Qdrant/Neo4j implementation details.

```text
BrainBinding
  ↓
KnowledgeAccessContract
  ├─ RelationalStoreContract
  ├─ VectorStoreContract
  ├─ GraphStoreContract
  ├─ SearchStoreContract
  ├─ ObjectStoreContract
  └─ MemoryStoreContract
```

## 10. Security architecture

- Supply Resolver decides package binding eligibility.
- UAG / Knowledge Access Policy decides concrete retrieval/action authority.
- Storage adapters enforce technical credentials and tenant boundaries.
- Evidence Ledger records the decision identity.

Reasoning permission is not action authority.

## 11. First implementation slice

Block ID: **FTH-BRAIN-SUPPLY-001**

Inputs:
- AgentBrainRequest
- candidate BrainPackageDescriptor set
- BrainSupplyPolicy

Output:
- BrainSupplyDecision

Required properties:
- deterministic;
- fail-closed;
- input-order independent;
- independent A-class and B-class checks;
- no vendor/network/database dependency;
- policy/version-bound identity;
- qualification harness.

## 12. Deferred architecture

Deferred:
- physical DB topology;
- vector benchmark;
- embedding selection;
- graph persistence;
- distributed deployment;
- production UAG integration;
- package signing;
- dynamic entitlement service.

## 13. Architecture gate

**ARCH PASS for FTH-BRAIN-SUPPLY-001.**
The A-class × B-class independence is now an explicit invariant and qualification target.
