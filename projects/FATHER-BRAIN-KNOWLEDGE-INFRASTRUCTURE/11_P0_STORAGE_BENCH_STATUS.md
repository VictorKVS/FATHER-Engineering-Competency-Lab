# P0 Storage Bench — qualification status

Date: 2026-11-14 local operator run.

## Environment

Preflight PASS:
- Windows 11 Pro;
- Intel Core i5-10400F, 6C/12T;
- RAM 31.84 GB;
- Docker Engine 29.9.2;
- Python 3.10.11.

## P0A — Image Acquisition

All required images are local.

| Candidate | Image | P0A |
|---|---|---|
| PostgreSQL | postgres:18-alpine | PASS |
| pgvector | pgvector/pgvector:0.8.7-pg18-trixie | PASS |
| Qdrant | qdrant/qdrant:latest | PASS |
| Neo4j | neo4j:2026.10.2 | PASS |
| OpenSearch | opensearchproject/opensearch:3.9.0 | PASS |

Image acquisition timings are supply-chain/network evidence only and are excluded from runtime performance comparison.

## P0B — Runtime Smoke

| Candidate | Startup | Memory | CPU snapshot | Functional smoke | Result |
|---|---:|---:|---:|---|---|
| PostgreSQL | 2.913 s | 97.07 MiB | 4.35% | PASS | PASS |
| pgvector | 2.042 s | 104.4 MiB | 5.59% | PASS | PASS |
| Qdrant | 1.750 s | 71.84 MiB | 0.16% | PASS | PASS |
| Neo4j | 19.572 s | 1.253 GiB | 19.36% | PASS | PASS |
| OpenSearch | 24.586 s | 1.484 GiB | 6.62% | PASS | PASS |

## Gate result

**P0B COMPLETE — 5/5 PASS.**

This gate proves only:
- image available;
- container starts;
- readiness is reached;
- minimal functional operation succeeds;
- basic runtime resource snapshot can be collected.

It does **not** prove:
- comparative performance;
- retrieval quality;
- scalability;
- durability;
- backup/restore;
- recovery;
- high availability;
- production suitability.

## Next gate

P1 Comparative Workload Benchmark:
- identical corpus/workload;
- ingest rate;
- index build;
- p50/p95/p99;
- throughput/QPS;
- concurrency;
- filtered retrieval;
- update latency;
- RAM/CPU/disk under load;
- restart/recovery;
- role-specific quality metrics.

Only P1/P2 evidence may be used to build qualified storage envelopes for Storage Selection Engine.
