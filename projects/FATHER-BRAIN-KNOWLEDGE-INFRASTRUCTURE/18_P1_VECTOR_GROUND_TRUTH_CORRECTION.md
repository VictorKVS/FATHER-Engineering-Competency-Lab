# P1 Vector Ground Truth Correction

Date: 2026-11-14

## Trigger

At profile M (100,000 vectors), Qdrant with `exact=true` achieved only about 0.86 Recall@10 against the pre-storage analytical double-precision reference.

An exact search cannot be used as an ANN quality oracle while simultaneously failing the oracle itself.

## Root cause

The synthetic S/M corpus placed vectors on a unit circle.

At 100,000 points, adjacent cosine distances become extremely small. Storage engines persist vector coordinates in finite precision (typically float32 for vector storage), so multiple theoretically distinct nearest neighbors become numerically tied or nearly tied after storage.

Therefore:

- the analytical pre-storage geometry is still mathematically correct;
- it is no longer a valid qualification oracle after finite-precision storage;
- ANN quality must be compared against exact search over the same persisted representation.

## Corrected qualification rule

### pgvector

Ground truth:
- disable ANN index scan;
- execute exact sequential cosine search over stored `vector(384)` values;
- store exact top-k IDs for each benchmark query.

ANN Recall@K:
- enable HNSW;
- compare HNSW result against that persisted exact top-k.

### Qdrant

Ground truth:
- query with `exact=true`;
- record exact top-k IDs from the persisted collection.

ANN Recall@K:
- query with HNSW;
- compare ANN result against the exact persisted top-k.

## Diagnostic metric

The benchmark may still record:

```text
theoretical_pre_storage_agreement
```

This measures how much finite-precision persistence changes the theoretical neighbor set.

It is diagnostic only and does not determine ANN PASS/FAIL.

## Quality gate

The quality gate remains unchanged:

```text
ANN Recall@10 >= 0.95
```

No threshold reduction is permitted.

## pgvector parameter boundary

The installed pgvector build reports:

```text
hnsw.ef_search valid range: 1 .. 1000
```

Therefore M tuning uses:

```text
300 / 500 / 800 / 1000
```

Values above 1000 are invalid for this tested build and are not benchmark candidates.

## Impact on scale ladder

This corrected ground-truth method must be used for M/L/XL vector qualification.

A profile is promoted only when:
- exact persisted ground truth succeeds;
- ANN Recall@10 >= 0.95;
- latency/resource evidence exists;
- configuration and image digest are recorded.
