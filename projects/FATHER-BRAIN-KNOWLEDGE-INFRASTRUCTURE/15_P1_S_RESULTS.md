# P1-S status after pgvector tuning

## REL-S

- PostgreSQL: PASS
- pgvector relational mode: PASS

## VEC-S

### Qdrant
PASS at default tested configuration:
- Recall@10 mean: 0.96
- Recall@10 min: 0.9
- p95: 16.1785 ms
- p99: 22.4657 ms

### pgvector
Initial ef_search=100 did not satisfy Recall@10 >= 0.95.

Tuning pass:
| ef_search | Recall@10 mean | p95 ms | Result |
|---:|---:|---:|---|
| 100 | 0.936667 | 1.6722 | FAIL |
| 150 | 0.936667 | 1.8429 | FAIL |
| 200 | 0.936667 | 1.8886 | FAIL |
| 300 | 0.953333 | 7.6939 | PASS |
| 400 | 0.953333 | 7.2980 | PASS |

Selected minimum passing configuration:

```text
pgvector
HNSW vector_cosine_ops
ef_search = 300
Recall@10 mean = 0.953333
p95 = 7.6939 ms
```

This is the first qualified operating point for pgvector in profile S.

## Interpretation

This does NOT mean pgvector is globally better than Qdrant.

For this exact S-profile:
- pgvector reaches the quality threshold with lower p95 latency at ef_search=300;
- Qdrant also passes quality and remains a valid vector candidate;
- larger M/L corpus, concurrency and recovery tests are still required.

## Next gate

P1-M:
- 100,000 records/vectors;
- same 384 dimensions;
- same top-k/reference logic;
- concurrency C1/C4/C16;
- ingest;
- p50/p95/p99;
- Recall@K;
- RAM/CPU/disk under load.

Only after M-profile can we begin forming useful qualified storage envelopes for normal B2/B3 sizing.
