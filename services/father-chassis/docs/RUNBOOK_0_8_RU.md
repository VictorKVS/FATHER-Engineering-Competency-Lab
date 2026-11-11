# FATHER Chassis 0.8 — квалификация локальной LLM

## Цель

После инфраструктурного прогона 0.7 подключить реальную локальную модель через OpenAI-compatible API и доказать полный маршрут:

`документ → RAG → evidence → локальная LLM → ответ → audit`.

## Настройка

В `.env`:

```env
FATHER_MODEL_BASE_URL=http://host.docker.internal:1234/v1
FATHER_MODEL_NAME=<точный id модели>
FATHER_MODEL_API_KEY=
```

Порт 1234 — пример. Он должен совпадать с локальным сервером модели.

## Проверка

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\llm_test.ps1
```

Проверяются доступность `/v1/models`, наличие выбранной модели, полный Knowledge workflow, evidence, trace_id и persistent audit.

## PASS

`LOCAL LLM QUALIFICATION: PASS`.
