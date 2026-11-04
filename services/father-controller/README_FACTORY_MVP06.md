# FATHER Factory MVP-06 — Primitive Release Line

This milestone closes the first complete factory loop:

Requirements -> Auto Assembly -> Product Factory -> Unified Bench -> Release.

A release is created only when Acceptance status is READY.

Package:
- product_spec.json
- bench_report.json
- build_report.json
- model_selection.json
- release_manifest.json
- READY.json

The release manifest stores SHA-256 hashes for packaged artifacts.
Verification detects missing or modified artifacts.

BLOCKED products do not receive a release folder.

This is a primitive local release line, not yet Docker/Kubernetes/CI-CD deployment.
