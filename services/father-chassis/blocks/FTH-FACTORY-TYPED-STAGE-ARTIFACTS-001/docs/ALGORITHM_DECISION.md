# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. raw dict + runtime key checks — rejected: semantics remain weak;
2. Pydantic models — viable, but would mix engineering-core contracts with validation framework and duplicate existing dataclasses;
3. frozen dataclasses + explicit serializer/registry — selected;
4. protobuf/Avro — deferred until cross-language/distributed need is proven.

Selected algorithm:
- define frozen dataclasses for missing stage payloads;
- reuse existing typed BusinessProcessSpec/AlgorithmSpec/ArchitectureSpec/TestContract/DevelopmentPacket;
- maintain static artifact schema registry;
- serializer converts dataclass recursively to canonical dict;
- deserializer is explicit per payload type/version;
- StageArtifact validates artifact_type + payload class at construction;
- persisted snapshot stores payload_schema_version + payload_data;
- restore selects schema adapter, reconstructs typed payload, then recomputes artifact hash.

Rationale:
strong typing with minimal dependency surface and full control of migration semantics.