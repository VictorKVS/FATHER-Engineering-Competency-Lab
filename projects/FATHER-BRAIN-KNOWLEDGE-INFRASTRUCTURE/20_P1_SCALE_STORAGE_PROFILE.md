# P1 Scale Storage Profile

## Trigger

The pgvector M build-tuning run failed with:

```text
DiskFull: could not write to file "pg_wal/xlogtemp.*": No space left on device
```

This is an infrastructure limit of the original benchmark compose, not a pgvector qualification result.

The original P0/S compose intentionally used 1 GiB tmpfs storage for fast isolated smoke/small-profile runs.

That storage model is not suitable for:
- repeated HNSW rebuilds at M;
- L = 1,000,000 vectors;
- XL = 10,000,000 vectors;
- WAL/index/temp-file growth.

## Decision

Keep the original compose unchanged for historical P0/S reproducibility.

Introduce a separate scale compose:

```text
benchmarks/brain-storage/compose.scale.yaml
```

M/L/XL use Docker named volumes:

- PostgreSQL -> `postgres-scale-data`
- pgvector -> `pgvector-scale-data`
- Qdrant -> `qdrant-scale-data`

Each benchmark runner still removes its volume with `docker compose down -v` after evidence is written.

## Evidence meaning

Results from tmpfs and named-volume profiles must not be merged as if they were identical storage conditions.

Scale evidence must record:

```text
storage_mode = docker_named_volume
compose_profile = scale
```

The DiskFull run is classified:

```text
ENVIRONMENT_LIMIT
not CANDIDATE_QUALITY_FAIL
```

It does not count against pgvector qualification.
