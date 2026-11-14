# P1-M pgvector qualification result

pgvector is qualified for profile M = 100,000 vectors.

## Minimal passing operating point

```text
m = 48
ef_construction = 256
ef_search = 1000
Recall@10 mean = 0.95
p95 = 53.8959 ms
```

## Preferred operating point for next scale step

```text
m = 48
ef_construction = 512
ef_search = 1000
Recall@10 mean = 0.952222
p95 = 34.7516 ms
```

The second profile costs more build time but gives more quality margin and substantially better measured p95 in this run, so it is the starting configuration for L=1,000,000.

## Important negative result

```text
m = 64
ef_construction = 512
Recall@10 mean = 0.941111
FAIL
```

Increasing HNSW connectivity did not monotonically improve quality.

This evidence is important for Storage Selection Engine: parameter size is not a proxy for quality.

## Promotion to L

Vector candidates entering L:

- pgvector: m=48, ef_construction=512, ef_search=1000
- Qdrant: m=16, ef_construct=100, hnsw_ef=64

L uses exact persisted ground truth for qualification.
