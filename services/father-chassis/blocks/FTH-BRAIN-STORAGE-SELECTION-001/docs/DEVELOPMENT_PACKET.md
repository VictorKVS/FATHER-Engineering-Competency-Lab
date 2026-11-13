# DEVELOPMENT_PACKET

## Authorized slice
Implement a deterministic abstract Storage Profile selector.

## Constraints
- Python stdlib only;
- no network;
- no database;
- no vendor-specific ranking;
- only declared profile envelopes;
- immutable dataclasses;
- explainable reject reasons;
- deterministic identity;
- fail closed.

## Files
- src/father/brain_factory/storage_selection.py
- src/father/brain_factory/__init__.py
- tests/test_storage_selection.py
- scripts/g7_brain_storage_selection_qualification_test.ps1

## Promotion
Only after local Windows qualification evidence.
