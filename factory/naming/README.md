# Naming & Terminology Layer

Public names must be replaceable without breaking architecture.

## Principle

Use a stable internal identifier for every important system, role, workspace, block, gate and external integration.

Example:

```
stable_id: ROLE-001
public_name: Knowledge & Reasoning Engineer
code_name: ALINA
```

If the public role is later renamed to something else, `ROLE-001` remains unchanged.

## What the registry tracks

- stable ID;
- public name;
- internal code name;
- previous names;
- aliases;
- entity type;
- known file/UI references;
- rename policy.

## Why

This supports:
- later IP/trademark/legal review;
- product rebranding;
- customer-specific terminology;
- white-label deployments;
- migration without breaking internal contracts;
- search of old names;
- generation of a rename impact report.

## Rule

Architecture, schemas and machine-to-machine contracts should prefer stable IDs.
Human-facing UI may resolve names from the registry.
