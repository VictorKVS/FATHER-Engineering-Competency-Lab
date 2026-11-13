# Business Process
Owner: Senior Business Analyst.

Goal:
prepare stable knowledge units for downstream graph/index/retrieval work without losing exact evidence lineage.

Input:
K3 StructuralDocument.

Output:
NormalizedChunkSet.

Business rules:
- every chunk traces to one StructuralDocument;
- chunk text is normalized deterministically;
- chunks preserve source unit references;
- chunks do not combine unrelated documents;
- policy/version is recorded;
- downstream uses chunk hash as stable identity.

KPIs:
- chunk without lineage: 0%;
- non-deterministic chunk hash: 0%;
- empty chunk: 0%;
- cross-document chunk merge: 0%.