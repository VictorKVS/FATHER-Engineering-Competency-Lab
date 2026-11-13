# Architecture
Owner: Principal/Solution Architect.

External Source
   ↓
Source Intake Adapter
   ↓
SourceIntakeService
   ├─ metadata validator
   ├─ SHA-256 fingerprinter
   ├─ duplicate detector
   └─ SourceIntakeRegistry
          ↓
SourceIntakeRecord
   ↓
Legal/Access Check
   ↓
Provenance Validation

Boundary:
Source Intake records what arrived.
It does not declare the source legally usable or knowledge-qualified.