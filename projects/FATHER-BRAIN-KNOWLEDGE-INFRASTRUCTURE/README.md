# FATHER Brain & Knowledge Infrastructure

<p align="center">
  <strong>Серийное производство, испытание и внедрение Brain Packages для агентов FATHER</strong>
</p>

<p align="center">
  <img src="./assets/brain_factory_architecture.svg" alt="FATHER Brain Factory architecture" width="100%">
</p>

---

## Статус проекта

| Gate | Состояние |
|---|---|
| Business Analysis | ✅ PASS |
| System Analysis | ✅ PASS |
| Architecture | ✅ PASS for FTH-BRAIN-SUPPLY-001 |
| Test Architecture | ✅ PASS for FTH-BRAIN-SUPPLY-001 |
| Development Packet | ✅ ISSUED |
| Senior Developer | ✅ IMPLEMENTED |
| Qualification | ✅ FTH-BRAIN-SUPPLY-001 PASS — 188 regression tests |
| Release | ⏳ Planned |

> Правило FATHER: **никакой реализации до прохождения аналитических, архитектурных и тестовых gate.**

---

## Зачем нужен этот проект

FATHER не должен создавать уникальную базу знаний заново для каждого агента.

Цель проекта — сделать знания отдельным серийным изделием:

```text
AGENT
+
BRAIN PACKAGE
+
MODEL
+
TOOLS
+
POLICY
=
PRODUCT
```

Brain Package должен быть:

- версионируемым;
- переносимым;
- воспроизводимым;
- тестируемым;
- безопасным;
- обновляемым;
- откатываемым;
- доказуемым через qualification evidence.

---

## Классы Brain

<p align="center">
  <img src="./assets/brain_classes.svg" alt="Brain classes B1-B6" width="92%">
</p>

| Class | Назначение | Пример |
|---|---|---|
| **B1 Embedded** | минимальный локальный мозг | FAQ, offline helper |
| **B2 RAG** | документный помощник | корпоративный RAG |
| **B3 Analytical** | профессиональный анализ | OSINT, ИБ, legal |
| **B4 Enterprise** | общая корпоративная knowledge fabric | multi-agent platform |
| **B5 High Assurance** | защищённые/критичные контуры | SOC, КИИ |
| **B6 Massive** | распределённая knowledge platform | Digital Twin, large OSINT |

---

## Agent Class × Brain Class

<p align="center">
  <img src="./assets/agent_brain_matrix.svg" alt="Agent Class by Brain Class matrix" width="92%">
</p>

**A-класс агента и B-класс мозга — независимые оси.**

Например:

```text
A3 Analyst + B3 Analytical        типичный вариант
A2 Standard + B5 High Assurance  допустимо при строгих требованиях доверия
A5 Security + B2 RAG             допустимо для небольшого защищённого RAG
```

Brain Supply Resolver проверяет обе оси отдельно и не делает скрытого правила A3 → B3.

---

## Производственная линия

```mermaid
flowchart LR
    A[Requirements] --> B[Brain Spec]
    B --> C[Source Admission]
    C --> D[Ingestion]
    D --> E[Normalization]
    E --> F[Entity / Relation]
    F --> G[Conflict / Version]
    G --> H[Canonical Knowledge]
    H --> I[Index Factory]
    I --> J[Retrieval Profile]
    J --> K[Qualification]
    K --> L[Brain Package]
    L --> M[Release]
    M --> N[Deploy]
    N --> O[Upgrade / Rollback / Revoke]
```

---

## Knowledge Factory roadmap

### Уже квалифицировано в chassis

```text
K1  Source Intake                         ✅
K2  Rights / Access / Provenance         ✅
K3  Structural Parser                    ✅
K4  Chunk Normalization                  ✅
K5  Entity / Relation Extraction         ✅
K6  Entity Resolution / Knowledge Graph  ✅
```

### Следующая производственная линия

```mermaid
flowchart TD
    K6[K6 Knowledge Graph] --> K7[K7 Conflict / Version Resolver]
    K7 --> K8[K8 Knowledge Canonicalization]
    K8 --> K9[K9 Index Factory]
    K9 --> K10[K10 Embedding Factory]
    K10 --> K11[K11 Retrieval Strategy Factory]
    K11 --> K12[K12 Retrieval Evaluator]
    K12 --> K13[K13 Brain Benchmark Lab]
    K13 --> K14[K14 Storage Adapter Standard]
    K14 --> K15[K15 Brain Packaging]
    K15 --> K16[K16 Brain Release Manager]
    K16 --> K17[K17 Compatibility Matrix]
    K17 --> K18[K18 Brain Migration]
    K18 --> K19[K19 Security Qualification]
    K19 --> K20[K20 Production Release]
```

---

## Storage is a capability, not a vendor

FATHER стандартизирует **интерфейс и qualification**, а не конкретного производителя.

```mermaid
flowchart TB
    APP[Brain / Retrieval Logic]

    APP --> R[RelationalStoreContract]
    APP --> V[VectorStoreContract]
    APP --> G[GraphStoreContract]
    APP --> S[SearchStoreContract]
    APP --> M[MemoryStoreContract]
    APP --> O[ObjectStoreContract]

    R --> R1[PostgreSQL]
    R --> R2[SQLite]

    V --> V1[pgvector]
    V --> V2[Qdrant]

    G --> G1[Neo4j]
    G --> G2[Other qualified adapter]

    S --> S1[OpenSearch]
    S --> S2[Other qualified adapter]

    M --> M1[Redis]
    M --> M2[Alternative]

    O --> O1[Local]
    O --> O2[S3-compatible]
```

---

## Как выбирается база

Не по популярности.

Factory должна учитывать:

- размер corpus;
- число объектов;
- vector count / dimensions;
- graph node/edge count;
- write rate;
- update frequency;
- retrieval mix;
- concurrency;
- latency SLO;
- availability;
- durability;
- security class;
- deployment target;
- cost ceiling;
- компетенции эксплуатации.

Результат — **ранжированные конфигурации с trade-offs**, а не один «любимый» стек.

---

## Knowledge Loading Profiles

| ID | Профиль | Для чего |
|---|---|---|
| KLP-01 | Static Documents | книги, регламенты, инструкции |
| KLP-02 | Continuous Documents | постоянно обновляемые репозитории |
| KLP-03 | DB Sync / CDC | корпоративные БД |
| KLP-04 | API Sync | внешние и внутренние API |
| KLP-05 | Web / OSINT | открытые источники |
| KLP-06 | Event Stream | события, телеметрия, SIEM |
| KLP-07 | Expert Curation | экспертное наполнение |
| KLP-08 | Generated Knowledge | производные знания с provenance |
| KLP-09 | Mixed | комбинированный профиль |

---

## Security-by-design

```mermaid
flowchart LR
    X[External Source]
    --> A[Source Admission]
    --> B[Ingestion Sandbox]
    --> C[Canonical Knowledge]
    --> D[Index / Storage]
    --> E[Retrieval Authorization]
    --> F[UAG]
    --> G[Agent]
```

Security проходит через весь lifecycle:

- source trust;
- rights/access;
- data classification;
- malicious document defense;
- poisoning resistance;
- provenance;
- integrity;
- tenant isolation;
- authorization;
- secrets/keys;
- backup/restore;
- signed releases;
- rollback/revocation;
- POLYGON adversarial tests.

---

## Метрики qualification

### Knowledge quality

- Recall@K
- Precision@K
- MRR
- NDCG
- Grounding
- Citation Accuracy
- Entity / Relation Accuracy
- Conflict Resolution Accuracy

### Performance

- latency p50 / p95 / p99
- throughput
- ingest rate
- index build time
- rebuild time

### Resources & economics

- CPU
- RAM
- GPU
- disk
- network
- cost/query
- cost/1M chunks
- maintenance effort

### Reliability & security

- availability
- backup / restore
- rollback
- poisoning resistance
- unauthorized retrieval blocking
- provenance integrity
- isolation violations

---

## FATHER engineering workflow

```mermaid
flowchart LR
    BA[Business Analyst ✅]
    --> SA[System Analyst ✅]
    --> AR[Architect ◉]
    --> TA[Test Architect]
    --> DP[Development Packet]
    --> DEV[Senior Developer]
    --> Q[Qualification]
    --> REL[Release]
```

Первый реализуемый блок **FTH-BRAIN-SUPPLY-001 QUALIFIED**. Следующий этап: Storage Profile / Storage Selection Engine.

---

## Артефакты проекта

- [01 — Business Analysis](./01_BUSINESS_ANALYSIS.md)
- [02 — System Analysis](./02_SYSTEM_ANALYSIS.md)
- [03 — Architecture](./03_ARCHITECTURE.md)
- [04 — Test Architecture](./04_TEST_ARCHITECTURE.md)
- [05 — Development Packet](./05_DEVELOPMENT_PACKET.md)
- [06 — Local Qualification Runbook](./06_LOCAL_QUALIFICATION_RUNBOOK.md)
- [07 — Architect & Operator Decision Guide](./07_ARCHITECT_DECISION_GUIDE.md)
- [08 — Bench Test Program](./08_BENCH_TEST_PROGRAM.md)

Следующие ожидаемые артефакты:

- `03_ARCHITECTURE.md`
- `04_TEST_ARCHITECTURE.md`
- `05_DEVELOPMENT_PACKET.md`
- qualification evidence
- ADR
- compatibility matrix
- benchmark matrix

---

## Definition of Done

Проект не считается завершённым, пока FATHER не докажет серийную линию:

```text
requirements
→ brain design
→ source loading
→ storage selection
→ build
→ benchmark
→ security qualification
→ package
→ release
→ deployment
→ upgrade / rollback
```

минимум для нескольких Brain classes и нескольких взаимозаменяемых storage implementations.

---

<p align="center">
  <strong>FATHER: стандартны контракты, испытания и качество — реализации могут меняться.</strong>
</p>
