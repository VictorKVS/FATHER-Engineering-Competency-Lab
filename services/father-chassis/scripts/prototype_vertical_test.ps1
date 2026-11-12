$ErrorActionPreference = "Stop"

Write-Host "[PROTOTYPE] 1. Modular core tests"
python -m pytest -q .\tests\test_modular_core_restore.py .\tests\test_access_control.py .\tests\test_kii_decision_trace.py .\tests\test_security_compliance_vertical.py .\tests\test_modular_access_runtime.py .\tests\test_capability_provider_manifest.py .\tests\test_agent_factory.py
if ($LASTEXITCODE -ne 0) { throw "PROTOTYPE CORE: FAIL" }

Write-Host "[PROTOTYPE] 2. Side-by-side modular API"
powershell -ExecutionPolicy Bypass -File .\scripts\modular_api_test.ps1
if ($LASTEXITCODE -ne 0) { throw "PROTOTYPE API: FAIL" }

Write-Host ""
Write-Host "FATHER WORKING PROTOTYPE VERTICAL: PASS"
