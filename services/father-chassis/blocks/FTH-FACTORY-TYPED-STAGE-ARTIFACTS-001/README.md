# Typed Stage Artifacts
Block ID: FTH-FACTORY-TYPED-STAGE-ARTIFACTS-001

Purpose: replace untyped cross-role payload dictionaries with versioned, validated engineering artifact schemas.

Scope:
- typed payload model for every engineering stage boundary;
- artifact_type -> payload type binding;
- deterministic serialization;
- schema versioning;
- fail-closed deserialization;
- compatibility with persistent workflow snapshots.

Non-goals:
- domain-specific product payloads;
- arbitrary plugin serialization;
- distributed schema registry.

Current target: B6 DEVELOPMENT READY before implementation; B9 after dedicated qualification.