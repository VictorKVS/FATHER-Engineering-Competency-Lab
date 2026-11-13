# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR CURRENT M2 BASELINE.

Immutable semantics:
- protected action without approved record must not execute;
- approval_id binds to one action;
- pending/approved state persists through StateStore;
- reasoning never equals authority;
- no father-controller dependency.

Implementation: src/father/core/approval.py
Integration: src/father/core/runtime.py; src/father/factory/executor.py
Tests: tests/test_factory_execution.py; tests/test_factory_persistence.py

Changes to states, authority, action binding, approver identity, revocation or expiration require upstream review before coding.