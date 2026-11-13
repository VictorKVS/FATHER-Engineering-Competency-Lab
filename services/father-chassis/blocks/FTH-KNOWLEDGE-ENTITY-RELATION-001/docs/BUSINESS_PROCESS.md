# Business Process
Owner: Senior Business Analyst.

Goal:
turn normalized knowledge chunks into typed, evidence-linked facts that downstream graph construction can consume.

Input:
K4 NormalizedChunkSet.

Output:
ExtractionSet containing EntityRecord and RelationRecord objects.

Business rules:
- every entity/relation must cite at least one chunk;
- no relation may reference unknown entity IDs;
- extraction confidence is explicit;
- extractor/version/policy identity recorded;
- inferred facts are not mixed with observed facts in v1.

KPIs:
- entity without evidence chunk: 0%;
- relation with dangling entity reference: 0%;
- extraction without extractor version: 0%;
- non-deterministic reference extractor output: 0%.