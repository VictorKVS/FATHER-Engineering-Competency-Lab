# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Approved implementation boundaries:
- new typed payload definitions may be introduced in engineering module;
- existing delivery_contract types are reused, not duplicated;
- StageArtifact payload changes from dict[str,Any] to registered typed payload;
- artifact schema registry is static/versioned in code for v1;
- persistence stores payload_schema_version + payload_data;
- restore reconstructs typed payload before accepting hash;
- raw dict payload is no longer valid for engineering stage handoff.

Compatibility:
tests/helpers must migrate to typed constructors.
No silent legacy dict compatibility at engineering role boundaries.

Implementation targets:
src/father/engineering/stage_artifacts.py
src/father/engineering/factory_orchestrator.py
tests/test_stage_artifacts.py
tests/test_factory_orchestrator.py