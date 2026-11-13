# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-GR-01 valid extraction sets -> BUILT.
AC-GR-02 exact same type/name entities merge.
AC-GR-03 merged node preserves all source entity/evidence IDs.
AC-GR-04 same name different type creates conflict and does not merge.
AC-GR-05 relations resolve to valid nodes.
AC-GR-06 duplicate equivalent relations deduplicate while preserving lineage.
AC-GR-07 dangling relation rejected.
AC-GR-08 same semantic inputs in different input order -> same graph_hash.
AC-GR-09 policy version changes identity.
AC-GR-10 no inferred edges.
AC-GR-11 full regression PASS.

Target:
G7 K6 ENTITY RESOLUTION GRAPH.