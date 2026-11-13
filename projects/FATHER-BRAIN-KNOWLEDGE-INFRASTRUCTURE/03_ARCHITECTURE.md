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

## 2. Agent supply model

An agent does not connect directly to a database.

```text
Agent / Task
   ↓
BrainSupplyRequest
   ↓
Brain Supply Resolver
   ├─ identity
   ├─ agent class
   ├─ role
   ├─ domain
   ├─ required capabilities
   ├─ supply mode
   ├─ tenant
   ├─ security clearance
   └─ compatibility policy
   ↓
AUTHORIZED BrainBinding
   ↓
Retrieval / Knowledge Access Boundary
   ↓
Storage adapters
```

## 3. Supply modes

The architecture recognizes separate supply modes:

- **BASELINE** — stable brain attached to an agent profile.
- **ROLE_SCOPED** — added because the active role requires it.
- **DOMAIN_SCOPED** — added for a specific knowledge domain.
- **TASK_SCOPED** — temporary brain for a task/workflow.
- **SESSION_SCOPED** — temporary brain for a controlled session.
- **INCIDENT_SCOPED** — security/operations brain bound to a specific incident.

A Brain Package explicitly declares supported supply modes.

## 4. Matching dimensions

No package is eligible unless all mandatory dimensions pass:

| Dimension | Rule |
|---|---|
| Release state | package must be QUALIFIED or RELEASED according to policy |
| Brain class | exact class in v1; no silent up-class/down-class |
| Agent class | agent class must be declared compatible |
| Role | request role must intersect allowed roles where restricted |
| Domain | requested domains must be covered |
| Capability | all required capabilities must be present |
| Supply mode | requested mode must be supported |
| Classification | agent must be authorized for package classification |
| Tenant | package must be global or match tenant |
| Compatibility | package compatibility policy must pass |
| Revocation | revoked/superseded package must not be selected |

## 5. Fail-closed decisions

The resolver returns one of:

- `BOUND`
- `NO_MATCH`
- `AMBIGUOUS`
- `REJECTED`

It never silently substitutes a “close enough” brain.

If two candidates remain equally eligible and deterministic ranking cannot distinguish them, v1 returns `AMBIGUOUS`.

## 6. Minimal sufficient selection

Within the exact requested Brain Class, ranking prefers:

1. exact tenant over global;
2. exact domain fit;
3. fewer unnecessary capabilities;
4. highest compatible semantic version only after compatibility rules;
5. deterministic package identity tie-break only when policy explicitly permits.

No larger Brain Class is selected merely because it has more capabilities.

## 7. Brain classes

- B1 Embedded
- B2 RAG
- B3 Analytical
- B4 Enterprise
- B5 High Assurance
- B6 Massive

Brain Class is not a security clearance. A B2 brain may be highly protected; a B5 designation describes assurance requirements, not permission to read arbitrary data.

## 8. Storage boundary

Brain Supply Resolver knows **capabilities and package identity**, not PostgreSQL/Qdrant/Neo4j details.

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

This preserves vendor independence.

## 9. Security architecture

Policy enforcement is split:

- Supply Resolver decides whether a package may be bound.
- UAG / Knowledge Access Policy decides whether a concrete retrieval/action is authorized.
- Storage adapters enforce technical credentials and tenant boundaries.
- Evidence Ledger records decision identity and evidence.

Reasoning permission is not action authority.

## 10. First implementation slice

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
- no vendor dependency;
- no network dependency;
- no database dependency;
- policy/version-bound identity;
- qualification harness.

## 11. Deferred architecture

Not in the first slice:

- physical DB topology;
- vector benchmark;
- embedding selection;
- graph persistence;
- distributed deployment;
- production UAG integration;
- package signing;
- dynamic entitlement service.

These remain later gates.

## 12. Architecture gate

Architecture is acceptable for the first slice when:

- supply semantics are explicit;
- agent/package matching dimensions are explicit;
- fail-closed behavior is explicit;
- Brain Class is separated from security clearance;
- storage is behind contracts;
- first implementation slice is bounded and testable.

**Decision: ARCH PASS for FTH-BRAIN-SUPPLY-001 → Test Architecture authorized.**
