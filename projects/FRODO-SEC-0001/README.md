# FRODO — LLM Knowledge Base / Security Auditor

**Проект:** FRODO / «Взломщик»; `FATHER-LLM-SEC-0001` — существующий проектный паспорт [LLM Red Team & Runtime Shield](../../docs/FUTURE/FATHER_LLM_SECURITY_0001.md).

**Текущий результат:** подготовлен **поисковый учебный Knowledge Pack** по LLM, **не** выпущен сетевой сканер, обученный атакующий агент или квалифицированный пентестер.

## Архитектура проекта

- **ALINA** — общий первоисточник подготовки: [BOOK-002](https://github.com/VictorKVS/alina-knowledge-worker/tree/feature/father-book-library-index-20261122/library/books/BOOK-002_Designing_LLM_Applications). НЕ создаём отдельную независимую энциклопедию, а импортируем read-only версионированную проекцию.
- **FRODO** — специализация «ИБ AI/LLM, агентные системы, RAG, инфраструктура»; сценарии из `knowledge/threat_catalog.json` только для контролируемых испытаний.
- **FATHER / UAG** — внешние политики и разрешения инструментов.
- **POLYGON** — независимый закрытый экзамен после обучения, безопасность, компетенции, регрессия и доказательства.
- **Sphinx/Enigma** — защитные роли (будущая интеграция).

## Объём зафиксированной базы

Источник: Suhas Pai, *Designing Large Language Model Applications*; **изучены главы 1–12, глава 13 ещё не изучена**. В базе есть 307 производных парафразированных узлов и 321 связей для всех разобранных глав. Это проектный слепок общего графа ALINA, **не подтверждение квалификации**. Содержимое книги не копировалось; ссылки на исходный PDF не публичны.

Важно: узлы и связи перенесены как **учебный материал**, не как верифицированная независимым экзаменатором истина. Веса — редакторская важность, не вероятность риска.

## Работа с базой

Python 3.10+; стандартная библиотека, без Docker, интернета, API и сканирования:

```powershell
cd projects/FRODO-SEC-0001
python kb.py stats
python kb.py search "prompt injection"
python kb.py search "RAG"
python kb.py chapter CH04
python kb.py threats
python kb.py check
python -m unittest discover -s tests -v
```

Результат команды `search` — поиск по названиям и определениям **локального JSON**, не семантический RAG. Новые источники ALINA будут импортироваться только через версионированную проверку provenance; машинное обучение весов пока не запускалось.

## Обязательный путь готовности

`KNOWLEDGE_BOOTSTRAPPED → CURRICULUM_DESIGNED → TRAINING_RUN → POLYGON_QUALIFIED → SECURITY_REVIEW → AUTHORIZED_SANDBOX_MVP`.

Пока **нет** команд сканирования сети или вызова реальных API. Направление будущего продукта: клиентский сканер с договором, scope/Rules of Engagement, изолированными диагностическими адаптерами, воспроизводимым evidence и отчётом.

## Разделение базы

`knowledge/llm_concepts.json` — весь фундамент LLM из BOOK-002 (общие темы не урезаны); `knowledge/llm_edges.json` — структурные связи; `knowledge/threat_catalog.json` — проектные категории угроз, **составленные FATHER, а не утверждения книги**; `knowledge/source_manifest.json` — происхождение; `curriculum/LLM_SECURITY_CURRICULUM.md` — программа подготовки; `qualification/POLYGON_EXAM_SPEC.md` — приёмка.

Для публикации/коммерческой эксплуатации потребуются ADR, лицензии, юридическое разрешение на обследование, защищённые логи, хеширование реальных исходников и end-to-end qualification.
