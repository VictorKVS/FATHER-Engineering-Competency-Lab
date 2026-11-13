# Business Process
Owner: Senior Business Analyst.

Goal:
turn one or more typed extraction sets into a graph where each node/edge is traceable to observed evidence and entity merges are explicit, reviewable and reproducible.

Input:
one or more K5 ExtractionSet objects.

Output:
KnowledgeGraphSnapshot.

Business rules:
- merge is a decision, not a side effect;
- exact canonical match may auto-merge under policy;
- conflicting type/name evidence must not silently merge;
- every node keeps source entity IDs;
- every edge keeps source relation IDs/evidence chunks;
- graph snapshot identity is deterministic.

KPIs:
- graph node without source entity lineage: 0%;
- graph edge without source relation lineage: 0%;
- silent conflicting merge: 0%;
- dangling edge endpoint: 0%.