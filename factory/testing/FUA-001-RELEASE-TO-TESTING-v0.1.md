# FUA-001 Release to Testing v0.1

Purpose:
complete the factory cycle from frozen snapshot through explicit human acceptance
and installation authorization for controlled testing.

Result on PASS:
- HUMAN_ACCEPTANCE = PASS
- INSTALLATION_GATE = PASS
- INSTALLATION_PERMIT = PASS
- status = INSTALLATION_APPROVED_FOR_TESTING
- production_ready = false
- next gates = PRODUCT_TEST, PILOT_TEST, PRODUCTION_READINESS_REVIEW

This gate never marks production_ready=true.
