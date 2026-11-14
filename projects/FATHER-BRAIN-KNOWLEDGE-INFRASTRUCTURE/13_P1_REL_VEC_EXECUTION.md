# P1 REL-S + VEC-S execution

This is the first executable P1 slice authorized by `12_P1_COMPARATIVE_WORKLOAD_SPEC.md`.

## Scope

- REL-S: PostgreSQL vs pgvector (relational/metadata behavior)
- VEC-S: pgvector vs Qdrant
- corpus: 10,000 deterministic records/vectors
- vector dimension: 384
- top-k: 10
- deterministic seed: 20261114
- measured repetitions: 3
- warm-up excluded from latency

## Vector reference model

Vectors keep the full 384-dimensional contract. The first two coordinates define a deterministic unit-circle geometry and remaining coordinates are zero.

This allows the benchmark to compute the exact cosine top-k reference analytically, without trusting another vector database as ground truth.

Measured vector evidence includes:
- ingest rate
- index build time when separately observable
- p50/p95/p99
- Recall@K mean/min
- Docker resource snapshots
- image digest
- evidence SHA-256

## Environment dependency

Host Python requires the existing optional chassis dependency:

```powershell
python -m pip install "psycopg[binary]>=3.2"
```

No NumPy or benchmark-specific external library is required.

## Run

```powershell
.\scripts\brain_storage_bench_p1_s.ps1 all
```

Or separately:

```powershell
.\scripts\brain_storage_bench_p1_s.ps1 rel
.\scripts\brain_storage_bench_p1_s.ps1 vec
```

## Qualification caveat

P1-S is a measured benchmark, not a universal vendor ranking.
Results are valid only for the recorded:
- hardware;
- image digest;
- configuration;
- corpus;
- workload;
- algorithm/index settings.

M-profile and recovery tests remain separate gates.
