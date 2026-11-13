# FATHER Engineering Delivery Standard

## Principle

Programming is not the stage where product semantics are invented.

A senior developer receives a constrained, approved development packet. If the packet is incomplete, contradictory or ambiguous, implementation is blocked and the work returns upstream.

## Mandatory production line

```text
BUSINESS OWNER / PRODUCT
    ↓
BUSINESS PROCESS DESIGN
    ↓
PROCESS OPTIMIZATION
    ↓
ALGORITHM DESIGN
    ↓
ALGORITHM REVIEW / APPROVAL
    ↓
ARCHITECTURE
    ├─ blocks
    ├─ states
    ├─ constants
    ├─ variables
    ├─ ownership
    ├─ data flow
    ├─ API / interfaces
    ├─ error contracts
    └─ SLO / resource boundaries
    ↓
SYSTEM ANALYSIS
    ├─ consistency
    ├─ completeness
    ├─ edge cases
    ├─ failure modes
    └─ corrections
    ↓
TEST CONTRACT
    ├─ what each block must output
    ├─ correctness
    ├─ completeness
    ├─ latency
    ├─ resource limits
    ├─ negative cases
    ├─ integration behavior
    └─ evidence required
    ↓
DEVELOPMENT PACKET APPROVED
    ↓
SENIOR DEVELOPER
    ↓
STATIC ANALYSIS
    ↓
UNIT / CONTRACT / INTEGRATION / REGRESSION
    ↓
SECURITY
    ↓
QUALIFICATION
```

## Senior developer constraints

The developer MUST NOT invent:

- variable names or meanings;
- API fields;
- message schemas;
- ownership of state;
- block responsibilities;
- constants that affect behavior;
- error semantics;
- security boundaries;
- acceptance thresholds.

The developer MAY propose an improvement, but it goes back through architecture/system-analysis approval before becoming implementation.

## Definition of Development Ready

Code work may start only when all are true:

1. business process approved;
2. algorithm approved;
3. architecture approved;
4. all inter-block variables and interfaces declared;
5. states/constants/errors declared;
6. system analyst approval present;
7. test contract approved;
8. acceptance metrics defined.

## Definition of Done

A block is not done because it executes.

It must prove:

- static correctness;
- declared interface compliance;
- unit behavior;
- contract behavior;
- integration behavior;
- negative/failure behavior;
- regression safety;
- security controls;
- performance/resource acceptance where relevant;
- evidence and traceability to the approved packet.

## Error prevention lesson from G7 M2

The undefined `recipe` variable in ProductRegistry was a process failure: implementation changed before a formal variable/interface contract and static undefined-name gate existed.

Preventive controls:

1. DevelopmentPacket fail-closed validation;
2. architecture-owned variable contracts;
3. tester-owned acceptance contract before implementation;
4. Ruff/Pyflakes undefined-name CI gate;
5. full regression;
6. runtime qualification.

The goal is not to catch trivial defects later. The goal is to make whole classes of defects structurally difficult to introduce.
