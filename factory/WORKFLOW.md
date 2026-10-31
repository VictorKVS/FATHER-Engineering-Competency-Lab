# FATHER Factory Workflow v0.1

## 01 Business Analysis
Преобразует замысел заказчика в формальную бизнес-модель.

## 02 System Analysis
Преобразует бизнес-модель в системные требования, компоненты, интерфейсы и данные.

## 03 Architecture
Формирует целевую архитектуру и распределение ответственности между компонентами.

## 04 Data & Knowledge
Проектирует данные, RAG, knowledge graph, provenance и lifecycle знаний.

## 05 AI / LLM Design
Определяет модели, роли LLM, routing, context, prompts, eval и fallback.

## 06 Security
Проектирует trust boundaries, policies, controls, threat model и security gates.

## 07 Development
Реализует компоненты, adapters, glue-code и конфигурацию.

## 08 QA
Проверяет unit/integration/functional/regression/eval.

## 09 DevSecOps
Сборка, CI/CD, контейнеризация, SBOM, deployment и observability.

## 10 Optimization
A/B, model/prompt/RAG/tool/config comparison, Best Known Configuration.

## 11 Polygon
Фиксированный RC проходит adversarial, failure, load, recovery и lifecycle испытания.

## 12 Release
Формирует готовый продукт, release package, документацию и acceptance.

## Правило возврата

Любой следующий цех может вернуть пакет предыдущему, если отсутствуют обязательные входные данные или нарушен контракт передачи.
