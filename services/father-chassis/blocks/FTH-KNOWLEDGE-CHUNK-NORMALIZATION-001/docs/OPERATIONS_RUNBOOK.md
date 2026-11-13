# Operations Runbook
Owner: DevSecOps/SRE.

Health:
normalizer/chunker version and policy available.

Upgrade:
changing normalization/chunk policy requires version bump and full regeneration.

Incident:
lineage/hash/policy mismatch -> REJECTED; never silently re-chunk under a different policy.

Rollback:
select prior policy version and regenerate from immutable K3 StructuralDocument.