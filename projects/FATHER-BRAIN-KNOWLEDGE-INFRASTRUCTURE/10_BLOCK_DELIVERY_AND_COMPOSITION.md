# 10 — Qualified Block Delivery & Agent Composition

## Цель

Когда FATHER собирает агента, он должен не "писать компонент заново", а:

1. определить требуемые capabilities;
2. найти квалифицированные блоки в Block Catalog;
3. проверить версии/совместимость/security;
4. выбрать delivery mode;
5. материализовать или привязать блок;
6. сформировать manifest;
7. проверить hashes/provenance;
8. квалифицировать собранное конечное изделие.

## Не все блоки надо физически копировать

Вводятся режимы поставки.

### EMBEDDED_COPY
Код/артефакты блока физически входят в пакет агента.

Применение:
- БПЛА;
- робот;
- offline edge;
- автономный appliance.

Плюсы:
- автономность;
- минимальные внешние зависимости.

Минусы:
- дублирование;
- обновление каждой копии отдельно.

### PACKAGE_DEPENDENCY
Агент получает версионированную package dependency.

Применение:
- обычные сервисы;
- Python package / container layer.

### SIDECAR
Блок поставляется рядом с агентом как отдельный локальный процесс/container.

Применение:
- локальный retrieval;
- proxy;
- policy/security helper.

### SHARED_SERVICE
Агент получает binding на общий квалифицированный сервис.

Применение:
- PostgreSQL;
- Qdrant cluster;
- graph/search;
- enterprise knowledge service.

## Правило выбора

```text
EDGE / OFFLINE
→ prefer EMBEDDED_COPY

LOCAL SERVICE COMPOSITION
→ PACKAGE_DEPENDENCY / SIDECAR

ENTERPRISE / MULTI-AGENT
→ prefer SHARED_SERVICE
```

Security policy может запретить отдельный режим.

## Qualified Block Package

Каждый готовый блок должен иметь:

- block_id;
- version;
- capabilities;
- qualification_status;
- canonical content hash;
- supported delivery modes;
- dependencies;
- config schema;
- security profile;
- provenance;
- source artifact/path or package coordinate.

## Сборка

```text
Requirement
  ↓
Block Matcher
  ↓
Qualified Block Catalog
  ↓
Compatibility Gate
  ↓
Delivery Mode Resolver
  ↓
Block Materializer
  ↓
Agent/Product Workspace
  ↓
Assembly Manifest
  ↓
End-product Regression
```

## Критический принцип

Квалификация блока не означает квалификацию агента.

После вставки блока весь агент должен пройти интеграционные/regression/security tests как конечное изделие.
