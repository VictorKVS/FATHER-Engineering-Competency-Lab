# FATHER FACTORY 1.0 RC1 — квалификационная программа

RC1 проверяет уже не отдельный компонент, а всю фабрику на целевой машине.

## Запуск

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\factory_rc_test.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build_rc_report.ps1
```

## Проверяемые контуры

1. холодный запуск из репозитория;
2. Docker / Compose;
3. PostgreSQL / pgvector;
4. Redis;
5. FATHER API;
6. health / readiness;
7. ingest;
8. RAG / evidence;
9. локальная LLM;
10. model routing / fallback;
11. OSINT / Knowledge product;
12. persistent audit;
13. Emergency Stop;
14. restart / recovery;
15. совместимость блоков;
16. source traceability;
17. BOM / reuse.

Полный RC PASS требует реальной локальной LLM. Если выставлен `FATHER_SKIP_REAL_LLM=1`, результат считается только инфраструктурным RC.

После реального RC PASS на целевой Windows-машине можно переводить G3 и G4 в PASS. Затем начинается G6: нагрузка, chaos, security gate, upgrade/rollback и endurance.
