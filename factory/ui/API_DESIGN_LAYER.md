# FATHER Assembly Table — API Design Layer v0.1

## Назначение
Первый визуальный слой Assembly Table показывает бизнес-модель изделия и фабрики. Пользователь видит узлы, потоки, пакеты, gates и возвратные петли. При переходе в API Design Layer любой поток раскрывается до контракта взаимодействия.

## Visual entities
### Node
Показывает участника, цех, систему, агента, сервис или внешний канал.

### Flow
Показывает передачу информации или управления.

### Package
Формальный набор артефактов, передаваемый между цехами.

### Gate
Условие допуска к следующему этапу.

### Rework
Возврат на предыдущий этап с дефектом.

## API Design interaction
При клике на Flow интерфейс должен раскрывать:
- producer
- consumer
- trigger
- protocol
- endpoint / event name
- payload schema
- data classification
- average/max size
- frequency / peak rate
- latency/SLA
- validation
- retry
- timeout
- idempotency
- authn/authz
- observability
- error contract
- test status

## Drill-down
L0 Factory
→ L1 Workshop
→ L2 Process
→ L3 Activity
→ Integration/API Flow
→ Payload / Schema
→ Runtime Event / Trace

## Status
NOT_DEFINED
DRAFT
VALIDATED
TESTED
SECURITY_VERIFIED
POLYGON_VERIFIED

## Principle
На схеме не должно быть безымянной стрелки. Любой Flow обязан иметь machine-readable contract.
