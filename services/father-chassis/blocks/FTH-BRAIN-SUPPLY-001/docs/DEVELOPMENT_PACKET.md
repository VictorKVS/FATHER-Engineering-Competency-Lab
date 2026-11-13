# DEVELOPMENT_PACKET

## Authorized implementation
Implement deterministic in-memory reference Brain Supply Resolver only.

## Files
- src/father/brain_factory/supply.py
- src/father/brain_factory/__init__.py
- tests/test_brain_supply.py
- scripts/g7_brain_supply_qualification_test.ps1

## Constraints
- Python stdlib only;
- no network;
- no database;
- immutable dataclasses;
- deterministic canonical hashes;
- fail closed;
- no implicit class upgrade/downgrade;
- no direct UAG/storage implementation in this slice.

## Acceptance
Implementation is only a qualification candidate until the Windows harness passes and evidence is generated.
