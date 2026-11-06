# TIMA — Lean Container Engineering / Docker Image Diet

## Назначение
Обязательный DevSecOps-паттерн для Тимофея (TIMA): уменьшать контейнерный образ до минимально достаточного runtime без потери совместимости, наблюдаемости и безопасности.

## Главный принцип
Не цель: "образ всегда <= 20 MB".

Цель:
- убрать всё, что не нужно в runtime;
- уменьшить attack surface;
- сократить время загрузки и запуска;
- уменьшить storage/registry traffic;
- сохранить воспроизводимость и совместимость;
- доказать безопасность и работоспособность тестами.

## Алгоритм TIMA
1. Зафиксировать исходный image:
   - image size
   - base image
   - package count
   - startup time
   - runtime memory
   - exposed ports
   - running user
   - CVE summary
   - SBOM status
2. Определить, что реально требуется в runtime.
3. Удалить build-only dependencies из финального слоя.
4. Применить multi-stage build.
5. Выбрать минимальный совместимый base image:
   - slim
   - distroless
   - alpine
   - scratch
   только если совместимость подтверждена.
6. Запускать процесс как non-root.
7. Не хранить secrets в image.
8. Сгенерировать SBOM.
9. Выполнить vulnerability scan.
10. Выполнить runtime smoke/integration tests.
11. Измерить startup time и image size повторно.
12. Сравнить baseline и optimized image.
13. Подписать/зафиксировать approved image.
14. Сохранить evidence.

## Container Gate
PASS только если:
- build succeeds
- runtime tests pass
- non-root or approved exception
- no embedded secrets
- SBOM generated
- critical vulnerabilities = 0 or formally accepted
- build-only dependencies absent
- image size justified
- startup time measured
- base image provenance recorded
- exposed ports justified

## Метрики
- image_size_mb
- package_count
- critical_cve_count
- high_cve_count
- startup_time_seconds
- runtime_memory_mb
- layer_count
- sbom_present
- non_root
- signed
- reproducible_build

## Сравнение вариантов
TIMA должен сравнивать варианты как инженерную оптимизацию:

Container Efficiency =
Security
+ Runtime Compatibility
+ Startup Speed
+ Reproducibility
+ Operability
- Excess Size
- Unused Packages
- Vulnerability Exposure

Минимальный image не считается лучшим, если ломает runtime или поддержку.

## Профили
### API / Gateway
Ожидается lean runtime.

### Python worker
Допустим slim runtime с только production dependencies.

### RAG worker
Размер может быть больше из-за библиотек retrieval/embedding.

### LLM / GPU worker
CUDA/runtime/model dependencies могут давать большой образ; размер должен быть обоснован, а не искусственно минимизирован.

## Evidence
Для каждого изменения сохранять:
- Dockerfile before/after
- image digest
- image size before/after
- SBOM
- vulnerability scan
- runtime test output
- startup benchmark
- reason for retained packages
- final gate result
