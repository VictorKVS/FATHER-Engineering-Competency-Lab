# Contracts

This module defines machine-readable obligations and guarantees.

## Contract classes

- component
- data
- security
- qualification
- ownership_provenance

## Core rule

A contract is not evidence. It defines what must be true.

Qualification evidence proves whether the contract was satisfied.

## Generic contract envelope

```json
{
  "contract_id": "CTR-...",
  "contract_type": "component",
  "version": "1.0.0",
  "subject_id": "SUBJECT-...",
  "provides": [],
  "requires": [],
  "constraints": [],
  "qualification_policy": "POLICY-...",
  "provenance": {
    "created_by": "...",
    "source_ref": "...",
    "parent_hash": "...",
    "content_hash": "..."
  }
}
```

FATHER-specific contracts must be implemented as profiles/adapters over this generic envelope.
