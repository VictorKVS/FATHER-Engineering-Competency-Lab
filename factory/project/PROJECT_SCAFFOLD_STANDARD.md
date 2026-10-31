# Canonical Project Scaffold

Every factory-created project uses the same internal chassis.

## Required root

    <PROJECT>/
    ├── project.yaml
    ├── canonical/
    ├── stages/
    │   ├── 000.yaml
    │   ├── 001.yaml
    │   ├── ...
    │   └── 100.yaml
    ├── artifacts/
    ├── agents/
    ├── algorithms/
    ├── knowledge/
    ├── models/
    ├── tools/
    ├── tests/
    ├── evidence/
    ├── releases/
    └── .factory/

The numeric stage identifier is immutable. Human-readable names may evolve.

A stage may be:
- LOCKED
- READY
- IN_PROGRESS
- READY_FOR_GATE
- APPROVED
- HOLD
- REJECTED
- NOT_APPLICABLE

NOT_APPLICABLE requires a recorded reason and approval.

No generated project may omit stage numbers. This gives every product the same manufacturing coordinate system from 000 through 100.