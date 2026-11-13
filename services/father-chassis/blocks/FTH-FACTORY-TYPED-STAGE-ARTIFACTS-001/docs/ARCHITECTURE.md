# Architecture
Owner: Principal/Solution Architect.

Agent output
   ↓
Typed Payload
   ↓
ArtifactSchemaRegistry
   ├─ artifact_type
   ├─ schema_version
   ├─ Python payload type
   ├─ serializer
   └─ deserializer
   ↓
StageArtifact
   ↓
FactoryEngineeringWorkflow
   ↓
StateStore snapshot

Boundaries:
- role contract chooses artifact_type;
- schema registry chooses allowed payload class;
- StageArtifact owns envelope metadata/hash;
- workflow owns stage authority;
- StateStore owns bytes/JSON persistence only.

No layer may silently coerce unknown dict fields into accepted semantics.