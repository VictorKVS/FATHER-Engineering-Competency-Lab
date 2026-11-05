# FATHER Novel RAG + Knowledge Base Model Bench

Один и тот же роман прогоняется через **все установленные Ollama-модели**.

## Что сравниваем

1. RAG по одинаковым чанкам и одинаковым вопросам.
2. Построение Narrative Knowledge Base в едином JSON-контракте.
3. Успешность выполнения.
4. Валидность JSON Knowledge Base.
5. Latency.
6. Полные ответы сохраняются для последующего человеческого сравнения качества.

## Почему retrieval одинаковый

На первом benchmark используется детерминированный lexical retrieval. Это намеренно: retrieval не должен меняться между моделями и искажать сравнение LLM.

Следующая версия может отдельно сравнить embedding/semantic retrieval.

## Входной роман

Положить UTF-8 текст:

`novel_benchmark/input/novel.txt`

Роман в GitHub автоматически не добавляется, чтобы benchmark мог использовать любой текст пользователя и чтобы случайно не публиковать защищённое авторским правом произведение.

## Запуск

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_NOVEL_MODEL_BENCH.ps1
```

Скрипт автоматически получает список моделей из Ollama `/api/tags`. Поэтому сравниваются все модели, реально установленные на машине.

## Evidence

- `evidence/novel_model_bench/novel_model_bench_partial.json` — обновляется после каждой модели;
- `evidence/novel_model_bench/novel_model_bench_latest.json` — полный отчёт;
- `evidence/novel_model_bench/novel_model_comparison.json` — технический ranking.

Технический ranking **не объявляет семантического победителя**. Качество анализа, точность фактов, причинность, character consistency и полнота Knowledge Base оцениваются отдельно.
