# FATHER Assembly Table v0.1

Первый интерактивный прототип модельного стола.

## Что реализовано
- слой 1: Business Model;
- последовательность основных цехов FATHER;
- кликабельные производственные узлы;
- кликабельные информационные потоки;
- Inspector справа;
- статусы DRAFT / READY / NOT_DEFINED;
- заготовка навигации по слоям;
- модель вынесена в model.js, UI не содержит бизнес-логики.

## Запуск
Открыть index.html локально в браузере.

## Следующие слои
1. BPMN L1/L2
2. API
3. Data
4. Agents/LLM
5. Infrastructure
6. Security
7. Tests/Polygon
8. Monitoring
9. Release/Sale

## Архитектурное правило
UI является визуализатором модели. Источник истины — machine-readable model/contracts в GitHub, а не ручная отрисовка.
