# Interfaces and Variables
Owner: Architect + System Analyst.

StageArtifact fields:
- artifact_id: str
- artifact_type: str
- payload_schema_version: int
- producer_agent_id: str
- payload: typed dataclass instance
- approved: bool
- evidence_refs: tuple[str,...]
- artifact_hash: str

Artifact schema registry entry:
- artifact_type: str
- schema_version: int
- payload_type: type
- serializer(payload) -> dict
- deserializer(dict) -> typed payload

Required mappings v1:
customer_request -> CustomerRequestPayload
BusinessProcessSpec -> BusinessProcessSpec
SystemAnalysisPackage -> SystemAnalysisPackage
AlgorithmSpec -> AlgorithmSpec
ArchitectureSpec -> ArchitectureSpec
TestContract -> TestContract
DevelopmentPacket -> DevelopmentPacket
ImplementationChange -> ImplementationChange
DeliveryQualification -> DeliveryQualification
QualificationDecision -> QualificationDecision

Errors:
unknown artifact type -> ValueError
unsupported schema version -> ValueError
wrong payload class -> TypeError/ValueError
malformed payload -> ValueError
hash mismatch -> ValueError.