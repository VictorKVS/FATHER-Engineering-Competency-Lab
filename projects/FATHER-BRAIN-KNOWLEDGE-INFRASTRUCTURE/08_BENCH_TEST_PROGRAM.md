# 08 — Brain Factory Bench Test Program

## Цель

Доказать, что выбранный Brain Class, Storage Profile и Brain Package реально подходят под целевой класс агента и deployment environment.

Испытания выполняются одинаково для reference implementations и альтернативных storage adapters.

---

# 1. Стенды

## STAND-E1 — Embedded / Edge

Цель:
B1 для БПЛА, робота, edge-компьютера.

Типовые ограничения:
- 2–8 CPU cores;
- 1–8 GB RAM;
- ограниченный SSD/eMMC;
- нестабильная сеть;
- ограниченный power budget.

Проверяет:
- startup;
- memory footprint;
- local latency;
- offline operation;
- recovery;
- power/resource behavior.

---

## STAND-R2 — Standard RAG

Цель:
B2 корпоративный/учебный RAG.

Проверяет:
- ingestion;
- retrieval quality;
- vector latency;
- multi-user concurrency;
- update/reindex;
- backup/restore.

---

## STAND-A3 — Analytical

Цель:
B3 аналитик.

Проверяет:
- vector + lexical + graph;
- entity/relation retrieval;
- conflict resolution;
- provenance;
- graph traversal;
- hybrid retrieval.

---

## STAND-E4 — Enterprise

Цель:
B4 multi-agent / multi-tenant.

Проверяет:
- HA;
- concurrency;
- tenant isolation;
- failover;
- horizontal scale;
- rolling update.

---

## STAND-S5 — High Assurance

Цель:
B5 protected / regulated.

Проверяет:
- authorization;
- tamper detection;
- signed release;
- immutable evidence;
- rollback controls;
- isolated operation;
- audit completeness.

---

## STAND-M6 — Massive

Цель:
B6 distributed high-scale.

Проверяет:
- sharding;
- replication;
- large ingest;
- distributed search;
- rebuild;
- recovery;
- scale efficiency.

---

# 2. Общая программа испытаний

Каждый кандидат проходит одинаковые группы.

## T01 Functional

Проверить:
- запись;
- чтение;
- обновление;
- удаление;
- version semantics;
- metadata filters;
- retrieval;
- export/import.

PASS:
все mandatory capability contracts выполнены.

---

## T02 Retrieval Quality

Метрики:
- Recall@K;
- Precision@K;
- MRR;
- NDCG;
- Grounding;
- Citation Accuracy.

Проверять минимум на:
- exact lookup;
- semantic paraphrase;
- multi-hop;
- conflict;
- stale version;
- negative/no-answer query.

---

## T03 Latency

Измерять:
- p50;
- p95;
- p99.

Режимы:
- cold;
- warm;
- cache hit;
- cache miss;
- filtered;
- unfiltered;
- concurrent.

---

## T04 Throughput

Нагрузки:
- 1;
- 10;
- 50;
- 100;
- 500;
- 1000 concurrent clients
где применимо.

Измерять:
- QPS;
- timeout rate;
- error rate;
- saturation point.

---

## T05 Ingest

Измерять:
- docs/sec;
- chunks/sec;
- vectors/sec;
- entities/sec;
- edges/sec;
- indexing lag.

---

## T06 Resource

Измерять:
- RAM idle;
- RAM p95 load;
- CPU idle/load;
- disk;
- network;
- GPU where applicable.

Для edge:
- startup RAM;
- peak RAM;
- binary/container footprint.

---

## T07 Power / Edge

Обязателен для БПЛА/роботов.

Измерять:
- average power;
- peak power;
- query energy cost;
- idle energy cost;
- thermal throttling behavior.

PASS определяется hardware profile.

---

## T08 Availability

Проверить:
- process kill;
- node loss;
- storage loss;
- network partition;
- restart;
- dependency loss.

---

## T09 Recovery

Проверить:
- backup;
- restore;
- integrity after restore;
- RPO;
- RTO.

Backup без успешного restore test = FAIL.

---

## T10 Update / Freshness

Измерять:
- source update → searchable latency;
- incremental index update;
- full rebuild;
- stale result rate.

---

## T11 Migration

Проверить:
- export canonical knowledge;
- rebuild in alternate storage;
- identity preservation;
- provenance preservation;
- retrieval regression.

---

## T12 Security

Проверить:
- unauthorized tenant;
- unauthorized classification;
- revoked release;
- malicious source;
- poisoning;
- metadata tamper;
- index tamper;
- credential misuse;
- privilege escalation.

---

## T13 Chaos

Проверить:
- random restart;
- slow dependency;
- corrupted cache;
- partial index;
- delayed event;
- duplicate ingest.

---

## T14 Cost

Считать:
- cost / 1M chunks;
- cost / 1M queries;
- cost / month;
- operator time;
- rebuild cost;
- migration cost.

---

# 3. Размеры benchmark corpus

```text
S   10k chunks
M   100k
L   1M
XL  10M
XXL 100M+ where supported
```

Для B1 допускаются S/M.
Для B2 — S/M/L.
Для B3 — M/L/XL.
Для B4–B6 — L/XL/XXL.

---

# 4. Edge-specific qualification

B1 для БПЛА/робота должен отдельно доказать:

- startup without network;
- local answer latency;
- memory ceiling;
- storage ceiling;
- no mandatory external service;
- recovery after abrupt power loss;
- data integrity;
- thermal stability;
- controlled degradation when storage is nearly full.

---

# 5. Comparative test

Каждый Storage Profile тестируется минимум двумя реализациями, когда это экономически оправдано.

Пример B2:

```text
Variant A:
PostgreSQL + pgvector

Variant B:
PostgreSQL + Qdrant
```

Сравнение:
- quality;
- p95;
- QPS;
- RAM;
- disk;
- operations;
- cost.

Победитель выбирается только в контексте workload profile.

---

# 6. Bench evidence

Каждый прогон должен сохранять:

- test_id;
- profile_id;
- candidate;
- software versions;
- hardware profile;
- corpus version;
- workload;
- metrics;
- PASS/FAIL;
- raw evidence references;
- timestamp;
- runner identity;
- hash.

---

# 7. Final decision output

```text
RECOMMENDED:
B2 + PostgreSQL + pgvector

WHY:
- target corpus: 200k chunks
- p95 target met
- Recall@10 target met
- RAM below limit
- lowest operations complexity

REJECTED:
B1 — quality degrades at corpus size
B3 — graph capability unused, +resource overhead
B4 — HA requirement absent

QUALIFICATION:
PASS
```

---

# 8. Promotion rule

Никакой Brain/Storage configuration не становится reference-рекомендацией FATHER, пока:

- не пройдены обязательные стенды;
- не получено evidence;
- не выполнен regression;
- не подтверждены limits;
- не описаны rejected alternatives.
