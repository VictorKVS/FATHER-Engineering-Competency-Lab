# P1-L Vector Corpus v1 Invalidation and Scale Corpus v2

## Trigger

The first L=1,000,000 vector run produced:

- pgvector Recall@10 mean = 0.133333
- Qdrant Recall@10 mean = 0.043333

Both engines completed queries without runtime errors, but both collapsed in ID-based recall.

## Root cause

The original vector corpus placed all objects on a 2D unit circle embedded in 384 dimensions.

At one million points, adjacent angular separation is approximately:

```text
2π / 1,000,000 ≈ 6.28e-6 radians
```

For cosine distance, neighboring values are then separated at roughly 1e-11 scale.

That is below practical float32 ranking resolution for persisted vectors, so many distinct IDs become numerically tied or nearly tied.

Result:

- exact and ANN can both return different but effectively equivalent neighbors;
- ID-set Recall@10 is no longer a valid ranking quality measure for this corpus at L/XL;
- the L vector result must not be interpreted as candidate failure.

## Classification

The first L vector evidence is classified:

```text
BENCHMARK_INVALID_FOR_RANKING
```

It is retained for provenance but excluded from candidate qualification.

REL-L remains valid and passed for PostgreSQL and pgvector relational mode.

## Scale Corpus v2

New deterministic scale corpus:

- 384 total dimensions;
- 32 active dimensions;
- deterministic modular mixing;
- L2 normalization;
- no dependency on random runtime state;
- exact persisted ground truth remains the qualification oracle.

Version:

```text
v2-deterministic-32d
```

## Gate sequence

1. Re-run M vector profile with Scale Corpus v2.
2. Confirm exact persisted reference + ANN Recall@10 >= 0.95.
3. Only then repeat L.
4. XL uses the same v2 corpus family.

This prevents spending large-scale test time on an invalid corpus.
