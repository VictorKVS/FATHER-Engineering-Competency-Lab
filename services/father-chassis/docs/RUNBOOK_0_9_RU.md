# FATHER Chassis 0.9 — квалификация первого продукта OSINT / Knowledge

## Цель

Проверить уже не отдельное шасси, а собранный из него продукт.

Маршрут:

`источники → нормализация → ingestion → RAG → evidence → model → claims → report → audit`.

## Запуск

После запуска FATHER:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\osint_product_test.ps1
```

Успех:

```text
OSINT PRODUCT QUALIFICATION: PASS
```

## Что проверяется

- несколько источников принимаются продуктом;
- источник получает или сохраняет `source_id`;
- metadata источника попадает в индексируемый текст;
- retrieval возвращает evidence;
- answer связан с evidence;
- claim получает статус `SUPPORTED` или `UNVERIFIED`;
- `trace_id` позволяет восстановить audit;
- BOM показывает, какие блоки переиспользованы;
- product workflow работает поверх общего FATHER Chassis.

## Статус G4

В текущей среде автоматические тесты доказывают программную интеграцию product pack.
Полный G4 будет закрыт только после такого же PASS на целевой машине с реальной локальной LLM.
