# FATHER Chassis / Factory — разработка

> English version: [README.md](README.md)

## Текущая версия: 0.6.0

**Автоматическая регрессия: 37/37 тестов PASS.**

FATHER Chassis — универсальное шасси и производственная основа для сборки разных AI/agent-продуктов из общих стандартных блоков.

### Что уже есть

- Configuration / State / Event Bus / Workflow;
- Model Router и fallback;
- RAG и Evidence;
- Tool Registry и RBAC;
- Guardrails;
- Human Approval;
- Emergency Stop;
- Audit и Trace;
- Factory / BOM / reuse-анализ;
- OSINT/Knowledge и ALINA/BOOKCRAFT как два разных product pack;
- FastAPI эксплуатационный API;
- persistent audit на SQLite;
- Dockerfile;
- Docker Compose с PostgreSQL/pgvector и Redis;
- OpenAI-compatible адаптер для локальной или облачной LLM.

## HTTP API 0.6

```text
GET  /health/live
GET  /health/ready
GET  /models
POST /ingest
POST /run
GET  /audit/{trace_id}
POST /approvals/{approval_id}
POST /control/stop
POST /control/resume
```

## Квалификационный статус

```text
G0 CODE EXISTS             PASS
G1 COMPONENT TESTED        PASS
G2 INTEGRATED              PASS
G3 CHASSIS QUALIFIED       IN PROGRESS
G4 PRODUCT QUALIFIED       IN PROGRESS
G5 REUSABLE                PASS
G6 INDUSTRIAL              NOT STARTED
```

G3 пока намеренно не закрываем: требуется реальный прогон на целевом Windows-компьютере с Docker Desktop, PostgreSQL/pgvector, Redis и локальной LLM.

## Доказательство повторного использования

- OSINT / Knowledge: reuse **93,75%**
- ALINA / BOOKCRAFT: reuse **75%**

## Целевая структура

```text
services/father-chassis/
├── src/          # исходный код
├── tests/        # автоматические испытания
├── config/       # конфигурации шасси
├── products/     # продуктовые пакеты
├── artifacts/    # qualification / BOM / reuse
├── docs/         # документация RU + EN
└── releases/     # релизные снимки
```

## Языковая политика

Ключевая документация ведётся полноценно **на русском и английском**. Русская версия обязательна и не должна быть сокращённым переводом.

## Следующий контрольный этап

0.7 будет направлен не на добавление декоративных функций, а на квалификацию реальной инфраструктуры и первого полного product workflow.
