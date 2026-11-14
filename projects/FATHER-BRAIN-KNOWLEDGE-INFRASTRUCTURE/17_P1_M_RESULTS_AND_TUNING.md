# P1-M first run and vector tuning decision

## REL-M — PASS

Both relational candidates passed at 100,000 records.

- PostgreSQL: PASS
- pgvector relational mode: PASS

The measured C1/C4/C16 runs had zero request errors and correctness PASS.

## VEC-M — tuning required

Initial scale run used:
- pgvector HNSW ef_search=300;
- Qdrant default vector query configuration.

Results:

| Candidate | Recall@10 mean | Quality gate |
|---|---:|---|
| pgvector | 0.833333 | FAIL |
| Qdrant | 0.856667 | FAIL |

Both completed requests without query errors, therefore this is treated as an ANN quality/configuration issue rather than a runtime failure.

## Decision

Do not advance vector qualification to L=1M until M is qualified.

The quality threshold remains Recall@10 >= 0.95.

### pgvector tuning

Test:
- ef_search 300
- 500
- 800
- 1200
- 2000

Select the minimum value that passes the quality gate.

### Qdrant tuning

Before measurement:
- wait for collection/index optimizer readiness;
- record indexed_vectors_count / points_count.

Control:
- exact=true must reproduce the deterministic reference.

ANN test:
- hnsw_ef 64
- 128
- 256
- 512
- 1024

Select the minimum value that passes the quality gate.

## Gate rule

If no tested configuration reaches Recall@10 >= 0.95, M remains unqualified for that candidate and the next step is index-build tuning (m / ef_construct), not lowering the quality threshold.
