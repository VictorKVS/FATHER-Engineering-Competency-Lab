# ARCHITECTURE

Input:
- ProductAssemblyRequest
- QualifiedBlockArtifact[]

Output:
- ProductMaterializationRecord

For EMBEDDED_COPY:
source artifact → verify canonical hash → copy into product workspace → verify copied hash → assembly manifest.

For PACKAGE_DEPENDENCY / SIDECAR / SHARED_SERVICE:
no source-tree copy; create deterministic binding record.

Security:
- target paths are generated from validated block_id/version;
- source hash must match;
- qualification status must be QUALIFIED;
- unsupported delivery mode fails closed;
- existing target conflict fails closed unless identical content.
