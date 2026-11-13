# System Analysis
Owner: Senior System Analyst.

Required artifact payload types:
1. CustomerRequestPayload
2. BusinessProcessSpec
3. SystemAnalysisPackage
4. AlgorithmSpec
5. ArchitectureSpec
6. TestContract
7. DevelopmentPacket
8. ImplementationChange
9. DeliveryQualification
10. QualificationDecision

Requirements:
TA-01 StageArtifact payload must be typed.
TA-02 artifact_type must map to exactly one allowed payload class per schema version.
TA-03 payload serialization must be deterministic.
TA-04 deserialization must reconstruct the declared type.
TA-05 artifact hash must include artifact type, payload schema version and serialized payload.
TA-06 unknown artifact type fails closed.
TA-07 wrong payload type fails closed.
TA-08 unknown schema version fails closed.
TA-09 persistence round trip preserves semantics.
TA-10 existing DevelopmentPacket nested types remain typed.

NFR:
no father-controller dependency; Python 3.10+; deterministic canonical JSON; backward migration points explicit.

Failure modes:
unknown type/version, malformed fields, enum/status mismatch, missing fields, hash mismatch.