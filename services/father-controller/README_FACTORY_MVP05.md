# FATHER Factory MVP-05 — Unified Bench / Acceptance Gate

Purpose: replace scattered readiness checks with one product acceptance result.

Current deterministic gate verifies:
- Product Spec validation
- Product Factory build
- runtime execution
- non-empty output
- Knowledge/RAG path returns at least one hit
- selected Brain matches Product Spec
- input/output adapters match the Product Spec
- tool profile is loaded

Output:
- READY when all required checks pass
- BLOCKED when any required check fails

This is the MVP acceptance gate. Future extensions will add security regression,
quality datasets, resource limits, latency thresholds, hybrid RAG tests and release comparisons.
