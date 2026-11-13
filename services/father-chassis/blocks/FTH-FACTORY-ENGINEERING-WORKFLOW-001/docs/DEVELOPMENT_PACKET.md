# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Immutable semantics:
- workflow authority survives restart;
- workflow_id isolates persisted state;
- restored artifacts are hash-verified;
- stage order and role ownership remain fail-closed;
- StateStore is persistence abstraction;
- no LLM may mutate stage authority directly.

Implementation target:
src/father/engineering/factory_orchestrator.py

Tests:
tests/test_factory_orchestrator.py
new persistence regression tests required.

Any change to snapshot semantics, hash validation or stage progression requires upstream review.