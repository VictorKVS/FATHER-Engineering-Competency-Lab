# FATHER Chassis 0.7 — инструкция первого квалификационного запуска на Windows

## Цель

Закрыть G3 не на словах, а реальным запуском на целевой машине.

## Порядок запуска

1. `git checkout father-chassis-development`
2. перейти в `services\father-chassis`
3. выполнить `powershell -ExecutionPolicy Bypass -File .\scripts\check_env.ps1`
4. выполнить `powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1`
5. выполнить `powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1`
6. выполнить `powershell -ExecutionPolicy Bypass -File .\scripts\recovery_test.ps1`

## Что считается PASS для G3

- Docker Engine доступен;
- PostgreSQL/pgvector healthy;
- Redis healthy;
- FATHER API ready;
- ingest работает;
- runtime отвечает;
- evidence возвращается;
- audit доступен по trace_id;
- emergency stop работает;
- после рестарта контейнера сервис возвращается в ready;
- knowledge сохраняется после рестарта.

## Важно

Если локальная LLM ещё не подключена, G3 может быть закрыт только как `CHASSIS INFRASTRUCTURE QUALIFIED`.
Полный `G3 CHASSIS QUALIFIED` потребует отдельного успешного прогона с реальной LLM.
