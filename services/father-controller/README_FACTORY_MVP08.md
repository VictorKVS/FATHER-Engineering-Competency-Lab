# FATHER Factory MVP-08 — Model Intelligence

Model Intelligence now lives inside FATHER Design Studio.

Core mechanism:
1. discover/create a model as CANDIDATE;
2. attach source-backed claims per field;
3. classify source type;
4. set confidence and verification status;
5. promote only confirmed/measured critical facts into normalized fields;
6. detect conflicts instead of silently overwriting data;
7. move sufficiently documented models to READY_FOR_BENCH;
8. later Bench/League can promote them to CHALLENGER or APPROVED.

Source classes:
- OFFICIAL_PRIMARY
- INDEPENDENT_BENCHMARK
- FATHER_LOCAL_MEASUREMENT
- DERIVED

Verification states:
- UNVERIFIED
- SOURCE_CONFIRMED
- FATHER_MEASURED
- CONFLICT
- STALE

The Design Studio UI exposes:
- Models catalog tab
- Model Intelligence workspace
- candidate creation
- source claim entry
- provenance fields and admission status

Automatic web collection is intentionally not trusted as approval by itself; collected claims still require source verification and/or FATHER measurement.
