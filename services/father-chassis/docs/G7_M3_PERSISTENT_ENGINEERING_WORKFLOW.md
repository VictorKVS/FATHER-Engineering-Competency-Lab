# FATHER G7 M3 — Persistent Engineering Workflow

M3 qualifies persistence of engineering governance, not only data persistence.

Acceptance:
- compile PASS;
- Ruff F821/F822/F823 PASS;
- full regression PASS;
- partial workflow restores after restart;
- next permitted stage is unchanged after restart;
- workflow IDs are isolated;
- BLOCKED history survives restart;
- tampered persisted StageArtifact is rejected by hash verification.

M3 PASS promotes FTH-FACTORY-ENGINEERING-WORKFLOW-001 from implementation/B6 baseline to B9 QUALIFIED.

M3 does not prove distributed multi-writer consensus, signatures/attestations or snapshot schema migrations.
