# FATHER Standard Specialist Package

Каждый специалист FATHER обязан иметь одинаковый каркас.

## Обязательные элементы
1. ROLE.md — роль, границы ответственности.
2. PROMPT.md — системный prompt.
3. ALGORITHM.md — детерминированный рабочий алгоритм.
4. RAG_MANIFEST.yaml — какие коллекции знаний разрешено использовать.
5. KNOWLEDGE_BASE.md — структура предметной базы знаний.
6. INPUT_CONTRACT.yaml — что специалист принимает.
7. OUTPUT_CONTRACT.yaml — что он обязан выдать.
8. CHECKLIST.md — DoD специалиста.
9. STATUS.yaml — maturity/status/version.
10. EVALS/ — как оценивается качество работы.
11. EXPERIENCE/ — подтверждённый опыт и ошибки.
12. API_HANDOFF.yaml — как результат передаётся следующему специалисту.

## Правило
Нельзя передавать downstream-специалисту свободный текст как единственный интерфейс.

Передаётся:
- machine-readable payload;
- human-readable artifact;
- schema;
- version;
- provenance;
- metrics;
- unresolved issues;
- evidence;
- gate status.
