# ADR-0001 — FATHER Factory uses Chassis + Standard Blocks + Configuration

Status: Accepted for Factory v0.1

## Decision

A FATHER product is assembled from:

```text
PRODUCT
=
CHASSIS
+ STANDARD BLOCKS
+ DOMAIN PACK
+ AGENTS
+ CONFIGURATION
+ PROJECT-SPECIFIC PART
```

The factory must prefer REUSE, then ADAPT, and only then BUILD.

## Sources

- SRC-FATHER-CONCEPT-001
- SRC-FATHER-LAB-001
- SRC-FATHER-README-001

See:

- `factory/registry/sources.json`
- `factory/docs/SOURCES_AND_PROVENANCE.md`

## Reason

The project explicitly rejects rebuilding the complete architecture for each new agent or product. Reusable components require standard contracts, compatibility rules and evidence.

## Consequences

Positive:

- common production line;
- comparable components;
- reusable security and observability;
- easier regression testing;
- provenance and evidence can be retained.

Cost:

- contracts and registries must be maintained;
- compatibility becomes an explicit engineering responsibility;
- a component cannot be called production-ready without integration evidence.
