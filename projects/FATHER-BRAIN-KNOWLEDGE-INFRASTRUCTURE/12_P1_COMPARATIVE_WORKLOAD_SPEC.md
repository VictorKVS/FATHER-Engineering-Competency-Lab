# P1 Comparative Workload Benchmark — Architecture & Test Contract

Status: APPROVED FOR IMPLEMENTATION
Date: 2026-11-14

## 1. Purpose

P1 converts P0B runtime-smoke evidence into measured capability envelopes.

P1 does not ask "which database is best overall".
It asks:

> Which qualified storage implementation is sufficient for a specific storage capability, workload, resource ceiling and SLO?

## 2. Fair-comparison rule

Candidates are compared only inside the same capability league.

### REL — Relational / Metadata
Candidates:
- PostgreSQL
- PostgreSQL + pgvector (relational baseline compatibility)

Workload:
- key lookup
- filtered lookup
- insert/update
- metadata join/filter

### VEC — Vector Retrieval
Candidates:
- pgvector
- Qdrant
- OpenSearch k-NN only after vector test contract is enabled

Workload:
- same vectors
- same dimensions
- same top-k
- same query vectors
- exact/ANN mode recorded explicitly
- filter/no-filter scenarios

### GRAPH — Graph Traversal
Candidates:
- Neo4j
- future graph adapters only when qualified

Workload:
- node lookup
- 1-hop/2-hop/3-hop traversal
- relation filter
- path query

### SEARCH — Lexical / Full-text
Candidates:
- OpenSearch
- future lexical adapters only when qualified

Workload:
- exact term
- multi-term
- filtered search
- top-k ranking

A single cross-vendor "winner" is forbidden.

## 3. Shared corpus profiles

Synthetic deterministic corpus generated from a fixed seed.

| Profile | Records/chunks |
|---|---:|
| S | 10,000 |
| M | 100,000 |
| L | 1,000,000 |

P1 begins with S and M. L is executed only if resource envelope remains safe.

Common fields:
- deterministic id
- title
- body/text
- domain
- classification
- timestamp
- numeric metadata
- tags
- graph relations
- vector generated from deterministic seed

Vector dimensions for first P1:
- 384

## 4. Workload phases

### P1.1 Load
Measure:
- total ingest time
- records/sec
- index build time
- final storage footprint
- peak/steady RAM where available

### P1.2 Warm-up
Warm-up queries are excluded from measured latency.

### P1.3 Single-client latency
Measure:
- p50
- p95
- p99
- mean
- errors

### P1.4 Throughput
Concurrency profiles:
- C1 = 1
- C4 = 4
- C16 = 16

Measure:
- completed ops/sec
- p95
- p99
- error rate

### P1.5 Updates
Measure:
- insert/update latency
- visibility/freshness delay where applicable

### P1.6 Restart/recovery
Measure:
- controlled stop
- restart-to-ready
- post-restart data verification
- query verification

## 5. Resource evidence

Record for each measured phase:
- CPU
- RAM
- disk usage
- block I/O
- network I/O where applicable

P0 snapshot values must not be reused as P1 load measurements.

## 6. Quality evidence

Performance without correctness is invalid.

### Vector
- Recall@K against deterministic exact/reference result
- top-k agreement
- filter correctness

### Graph
- expected node/path result correctness

### Search
- expected document retrieval
- deterministic test query assertions

### Relational
- row/result correctness
- update visibility

## 7. Repetition policy

Each measured scenario:
- warm-up first;
- minimum 3 measured repetitions;
- preserve individual runs;
- report median plus p50/p95/p99 where meaningful;
- do not hide failed runs.

## 8. Isolation

Candidates execute sequentially, not concurrently.

Before every candidate:
- previous candidate stopped;
- candidate-specific data lifecycle recorded;
- image pull prohibited;
- configuration hash recorded.

Host fingerprint is included in every benchmark bundle.

## 9. Evidence envelope

Each qualified result must contain:

```text
candidate_id
software/image version
image digest
hardware profile
capability league
corpus profile
record/vector/node count
vector dimensions
concurrency
configuration
ingest rate
index build time
latency p50/p95/p99
throughput
error rate
quality metrics
RAM
CPU
disk
restart time
PASS/FAIL
limits
evidence hash
```

## 10. P1 promotion rule

A candidate receives a P1 capability envelope only when:
- functional correctness PASS;
- workload completed;
- required quality PASS;
- no unrecorded errors;
- resource evidence exists;
- result is reproducible;
- evidence bundle is hashed.

No P1 envelope means Storage Selection Engine must not use performance claims for that candidate.

## 11. Initial execution order

1. REL-S: PostgreSQL, pgvector
2. VEC-S: pgvector, Qdrant
3. GRAPH-S: Neo4j
4. SEARCH-S: OpenSearch
5. repeat viable leagues at M profile
6. only then evaluate L profile

## 12. Gate

P0A: PASS
P0B: PASS 5/5
P1 Architecture/Test Contract: PASS
P1 implementation: AUTHORIZED
P1 measured qualification: PENDING
