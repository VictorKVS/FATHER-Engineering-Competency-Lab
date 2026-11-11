# FATHER Chassis / Factory — разработка

> English version: [README.md](README.md)

## Текущий кандидат: 1.0.0rc1

**Локальная автоматическая регрессия: 53/53 теста PASS.**

RC1 — первый кандидат на FATHER FACTORY 1.0. Он объединяет универсальное шасси, reusable blocks, локальную LLM-интеграцию, OSINT/Knowledge product pack, recovery, Emergency Stop, fallback, compatibility checks и единую квалификационную программу.

## Статус

```text
G0 CODE EXISTS                  PASS
G1 COMPONENT TESTED             PASS
G2 INTEGRATED                   PASS
G3 CHASSIS QUALIFIED            PENDING TARGET WINDOWS RC
G4 PRODUCT QUALIFIED            PENDING TARGET WINDOWS RC
G5 REUSABLE                     PASS
G6 INDUSTRIAL                   NOT STARTED
```

## Следующий обязательный этап

На целевом Windows-компьютере:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\factory_rc_test.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build_rc_report.ps1
```

Полный PASS требует реальной локальной LLM. После этого G3 и G4 можно переводить в PASS.

Русская программа: [docs/FACTORY_1_0_RC_RU.md](docs/FACTORY_1_0_RC_RU.md)
