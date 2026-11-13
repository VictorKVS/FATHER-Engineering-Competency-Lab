# 09 — Real Storage Bench Execution

## Цель

После qualification абстрактного Storage Selection Engine перейти от декларативных профилей к **измеренным профилям на реальном компьютере**.

Никакое утверждение "Qdrant быстрее", "pgvector компактнее", "Neo4j лучше для графа" не принимается без одинакового стенда и evidence.

## Последовательность

```text
Hardware Inventory
→ Environment Check
→ Baseline SQLite
→ PostgreSQL
→ PostgreSQL + pgvector
→ Qdrant
→ Graph candidate
→ Search candidate
→ Combined profiles
→ Compare
→ Qualified Envelope
→ Storage Catalog
```

## Фаза 1 — Hardware inventory

Сохраняем:
- CPU / cores / threads;
- RAM;
- available disk;
- OS;
- Python;
- Docker availability/version;
- optional GPU;
- filesystem;
- timestamp.

Результат привязывается ко всем benchmark evidence.

## Фаза 2 — одинаковые corpus/workload

Минимальные наборы:
- S: 10k chunks;
- M: 100k;
- L: 1M where hardware permits.

Каждый кандидат получает один и тот же:
- corpus seed;
- chunk size distribution;
- metadata fields;
- query set;
- concurrency plan.

## Фаза 3 — измерения

Для каждого кандидата:
- install/start time;
- idle RAM;
- peak RAM;
- disk footprint;
- ingest rate;
- index build time;
- p50/p95/p99;
- QPS;
- filtered search;
- update latency;
- restart/recovery;
- backup/restore where applicable.

## Фаза 4 — роли систем

### SQLite
Baseline для B1/EDGE:
- компактность;
- offline;
- zero-service deployment;
- relational/local metadata.

### PostgreSQL
System-of-record baseline:
- transactions;
- metadata;
- structured state;
- operational simplicity.

### pgvector
B2 single-database candidate:
- relational + vector in one service;
- lower operational complexity than separate vector service.

### Qdrant
Specialized vector candidate:
- separate vector workload;
- compare only on measured workloads.

### Graph candidate
Needed only where graph traversal / relationship workload is part of requirements.

### Search candidate
Needed only where lexical/hybrid/search analytics justify a separate engine.

## Фаза 5 — qualified envelope

После стенда создаётся измеренный envelope:

```text
candidate_id
software_version
hardware_profile
corpus_profile
max_tested_chunks
max_tested_concurrency
p95/p99
ingest_rate
RAM
disk
restart_time
quality metrics
limits
PASS/FAIL
evidence_hash
```

Storage Selection Engine использует только QUALIFIED envelopes.

## Главное правило

Сначала реальный benchmark → потом рекомендация архитектору.

Не наоборот.
