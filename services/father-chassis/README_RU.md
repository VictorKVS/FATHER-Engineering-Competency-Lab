# FATHER Chassis / Factory — разработка

> English version: [README.md](README.md)

## Текущая версия: 0.8.0

**Регрессия: 44/44 теста PASS.**

FATHER Chassis — универсальное шасси и производственная основа для сборки различных AI/agent-продуктов из общих стандартных блоков.

## Что добавлено в 0.8

- профиль локальной OpenAI-compatible LLM;
- probe `/models/local/probe`;
- квалификационный endpoint `/qualification/knowledge`;
- PowerShell-тест реальной локальной модели;
- полный маршрут `document → RAG → evidence → LLM → audit`;
- русская и английская инструкция квалификации.

## API

```text
GET  /health/live
GET  /health/ready
GET  /models
GET  /models/local/probe
POST /ingest
POST /run
POST /qualification/knowledge
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
G3 CHASSIS QUALIFIED       PENDING WINDOWS + REAL LLM
G4 PRODUCT QUALIFIED       IN PROGRESS
G5 REUSABLE                PASS
G6 INDUSTRIAL              NOT STARTED
```

G3 намеренно не закрывается до реального прогона на целевом Windows-компьютере.

## Локальная LLM

В `.env` задаются:

```env
FATHER_MODEL_BASE_URL=http://host.docker.internal:1234/v1
FATHER_MODEL_NAME=<точный id модели>
FATHER_MODEL_API_KEY=
```

После запуска FATHER:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\llm_test.ps1
```

PASS: `LOCAL LLM QUALIFICATION: PASS`.

Подробно: [RUNBOOK_0_8_RU.md](docs/RUNBOOK_0_8_RU.md).
