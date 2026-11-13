# P0 Storage Bench — first real run status

Date: 2026-11-14 local operator run.

## Environment

Preflight PASS:
- Windows 11 Pro;
- Intel Core i5-10400F, 6C/12T;
- RAM 31.84 GB;
- Docker Engine 29.9.2 available;
- Python 3.10.11.

## Candidate status

| Candidate | Result | Interpretation |
|---|---|---|
| PostgreSQL 18 | PASS | runtime functional smoke passed |
| pgvector | ENVIRONMENT_NETWORK_BLOCKED | Docker Hub blob transfer timed out before image became local |
| Qdrant | ENVIRONMENT_NETWORK_BLOCKED | Docker Hub auth/TLS timeout before image launch |
| Neo4j | ENVIRONMENT_NETWORK_BLOCKED | Docker Hub auth/TLS timeout before image launch |
| OpenSearch | ENVIRONMENT_NETWORK_BLOCKED | Docker Hub auth/TLS timeout before image launch |

## Important correction

The first PostgreSQL record reported 441.715 seconds as startup, but the same run spent about 436 seconds pulling the image.

Therefore that value is **not accepted as database startup latency**.

Benchmark architecture is corrected:

```text
P0A Image Acquisition
  ↓
all images local
  ↓
P0B Runtime Smoke
  ↓
startup time / RAM / CPU / functional smoke
```

P0B now uses `--pull never`, so network/image acquisition cannot contaminate runtime measurements.

## Qualification rule

Network failure during image acquisition is not a product FAIL.
Candidate product tests begin only when its required image is locally available and P0B starts the container.
