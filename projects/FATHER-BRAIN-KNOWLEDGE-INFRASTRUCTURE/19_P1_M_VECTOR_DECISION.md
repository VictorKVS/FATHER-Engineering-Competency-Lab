# P1-M vector decision after corrected ground truth

## Qdrant

M profile is qualified at the first tested HNSW search point:

```text
100,000 vectors
384 dimensions
HNSW m=16
ef_construct=100
hnsw_ef=64
Recall@10 mean=0.98
exact control=1.0
```

This becomes the current M operating point.

## pgvector

M remains unqualified after search-only tuning:

```text
ef_search 300..1000
Recall@10 mean = 0.886667
```

Because increasing ef_search does not improve recall, the next gate is index-build tuning rather than further search tuning.

Official pgvector HNSW controls:
- m: graph connectivity;
- ef_construction: construction candidate list;
- higher ef_construction can improve recall at the cost of build/insert time;
- ef_search affects query-time candidate breadth.

## Build tuning matrix

The next run evaluates:

```text
m=16, ef_construction=64
m=16, ef_construction=128
m=16, ef_construction=256
m=32, ef_construction=128
m=32, ef_construction=256
m=32, ef_construction=512
m=48, ef_construction=256
m=48, ef_construction=512
m=64, ef_construction=512
```

All are queried with ef_search=1000 to test whether graph construction, rather than query breadth, is the quality bottleneck.

Ground truth is exact search over persisted pgvector values before the ANN index is created.

## Promotion rule

- Qdrant may progress to L after its M concurrency envelope is incorporated.
- pgvector may progress to L only if a build configuration reaches Recall@10 >= 0.95.
- If none does, pgvector receives a documented M quality boundary for this corpus/index family rather than a false PASS.
