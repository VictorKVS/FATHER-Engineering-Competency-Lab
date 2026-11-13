# 07 — Architect & Operator Decision Guide

## Назначение

FATHER не должен выдавать только результат вида:

```text
Выбран профиль: B2
Storage: PostgreSQL + pgvector
```

Платформа обязана объяснить **почему** выбран именно этот вариант, какие альтернативы рассматривались, почему они хуже, какие компромиссы приняты и какие испытания должны подтвердить решение.

---

# 1. Формат архитектурного решения

Каждый автоматический выбор Brain Profile должен сопровождаться:

1. выбранным Brain Class;
2. выбранным Storage Profile;
3. workload assumptions;
4. ресурсными ограничениями;
5. требованиями latency / throughput;
6. требованиями durability / availability;
7. security class;
8. ranking alternatives;
9. rejected alternatives;
10. explanation;
11. required benchmark;
12. confidence / evidence state.

---

# 2. Пример объяснения оператору

```text
Рекомендуется B1 Embedded.

Почему:
- устройство работает на борту БПЛА;
- доступная RAM ограничена;
- сетевое соединение нестабильно;
- corpus мал;
- требуется локальная работа;
- latency должна быть минимальной;
- отказ внешней БД недопустим.

Рекомендуемый storage:
SQLite + local object cache.

Почему не B2:
- отдельный vector service увеличит RAM/CPU;
- усложнит deployment;
- повысит энергопотребление;
- даст мало преимущества при малом corpus.

Почему не B3:
- graph/vector/search stack избыточен;
- больше storage footprint;
- больше сервисов и точек отказа.

Условие допуска:
должны быть пройдены EDGE-S1, POWER-S1, LATENCY-S1 и RECOVERY-S1.
```

---

# 3. Классы и типовые области применения

## B1 — Embedded

### Где применять
- БПЛА;
- мобильные роботы;
- edge-сенсоры;
- автономные устройства;
- локальные offline helpers;
- небольшие knowledge modules.

### Почему
- минимальный storage footprint;
- минимум процессов;
- низкое энергопотребление;
- быстрое локальное обращение;
- работа без сети;
- простое восстановление.

### Типовая реализация
```text
SQLite
Local Files
Optional compact local vector index
```

### Когда B1 уже мало
- corpus быстро растёт;
- нужен semantic retrieval по большим массивам;
- требуются сложные фильтры;
- много одновременных запросов;
- требуется полноценный graph layer.

---

## B2 — RAG

### Где применять
- корпоративные помощники;
- инструкции;
- регламенты;
- документация;
- учебные агенты;
- support assistants.

### Почему
B2 добавляет semantic/vector retrieval без enterprise-сложности.

### Типовая реализация
```text
PostgreSQL
+
pgvector
+
Object Store
```

или при росте vector workload:

```text
PostgreSQL
+
Qdrant
+
Object Store
```

### Почему B1 может быть недостаточен
- хуже масштабирование retrieval;
- меньше возможностей фильтрации;
- сложнее обеспечивать multi-user concurrency.

### Почему B3 может быть избыточен
- graph engine не нужен;
- лишняя operational complexity;
- больше RAM/CPU/storage;
- дороже сопровождение.

---

## B3 — Analytical

### Где применять
- OSINT;
- ИБ;
- Threat Intelligence;
- legal analysis;
- scientific research;
- расследования;
- multi-source analytics.

### Почему
Нужны не только документы, но и:
- сущности;
- связи;
- версии;
- конфликты;
- provenance;
- graph traversal;
- hybrid retrieval.

### Типовая реализация
```text
PostgreSQL
+
Qdrant
+
Graph Store
+
Object Store
+
optional Redis
```

### Почему B2 мало
- vector retrieval не выражает сложные отношения;
- слабее конфликтный/версионный анализ;
- меньше возможностей для graph reasoning.

### Почему B4 избыточен
Если нет multi-tenant/HA/large-scale требований, distributed infrastructure не оправдана.

---

## B4 — Enterprise

### Где применять
- много агентов;
- много пользователей;
- shared knowledge fabric;
- high availability;
- enterprise multi-tenant.

### Почему
Нужны:
- HA;
- horizontal scale;
- tenant isolation;
- centralized governance;
- shared storage services.

### Типовая реализация
```text
PostgreSQL HA
Vector cluster
Graph cluster
Search cluster
Object Storage
Redis
Event Bus
```

---

## B5 — High Assurance

### Где применять
- SOC;
- КИИ;
- критические системы;
- закрытые контуры;
- регулируемые среды.

### Отличие от B4
Не обязательно больше по размеру.
Главное отличие — **уровень доверия и контроля**.

Требуются:
- signed releases;
- immutable evidence;
- fail-closed authorization;
- strong isolation;
- tamper detection;
- controlled rollback;
- auditability.

---

## B6 — Massive

### Где применять
- глобальный OSINT;
- Digital Twin;
- massive research corpus;
- high-ingest distributed systems.

### Почему
Нужны:
- sharding;
- replication;
- distributed ingestion;
- tiered storage;
- massive index build;
- distributed graph/search.

---

# 4. Матрица рекомендаций

| Условие | Предпочтение |
|---|---|
| RAM < 2 GB, offline, малый corpus | B1 |
| Edge device / БПЛА / робот | B1 |
| 10k–500k chunks, простой RAG | B2 |
| 500k–10M chunks, semantic retrieval | B2/B3 |
| Нужен graph / conflict / provenance analysis | B3 |
| Много агентов и tenants | B4 |
| Критичная/регулируемая среда | B5 |
| Очень большие distributed workloads | B6 |

Это стартовые правила, а не вечные числовые границы. Они должны уточняться benchmark evidence.

---

# 5. Аргументация выбора

Каждый выбор должен объясняться минимум по 8 осям:

| Ось | Что объясняем |
|---|---|
| Latency | почему профиль укладывается в p95/p99 |
| Throughput | выдерживает ли concurrency/RPS |
| RAM | помещается ли на целевой платформе |
| CPU/GPU | достаточны ли вычислительные ресурсы |
| Storage | размер corpus + индексов |
| Power | важно для БПЛА/роботов/edge |
| Reliability | сколько компонентов может отказать |
| Operations | сложность обслуживания |

Плюс:
- стоимость;
- масштабирование;
- безопасность;
- переносимость;
- восстановление.

---

# 6. Decision Score

Архитектор получает не только решение, но и score:

```text
FIT SCORE
=
Quality Fit
+ Performance Fit
+ Resource Fit
+ Security Fit
+ Reliability Fit
+ Cost Fit
+ Operations Fit
```

Вес каждой группы задаётся профилем продукта.

Пример БПЛА:

```text
Resource Fit        25%
Power Fit           20%
Latency             20%
Reliability         15%
Security            10%
Quality             10%
```

Пример Enterprise:

```text
Availability        20%
Scalability         20%
Security            20%
Quality             15%
Performance         15%
Cost                10%
```

---

# 7. Обязательное объяснение rejected alternatives

Платформа обязана выводить:

```text
B1 rejected:
retrieval quality target not met at target corpus.

B2 selected:
meets quality + latency with acceptable resource cost.

B3 rejected:
graph capability unused; operational cost higher.

B4 rejected:
HA/distributed requirements absent.
```

Без такой аргументации автоматический выбор не считается архитектурным решением.

---

# 8. Human override

Архитектор может изменить автоматическую рекомендацию.

Но override должен содержать:
- причину;
- автора;
- время;
- affected constraints;
- risk acceptance;
- required additional tests.

Override без evidence переводит решение в статус `EXCEPTION_PENDING_QUALIFICATION`.
