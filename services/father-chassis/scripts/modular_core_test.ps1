$ErrorActionPreference = "Stop"

Write-Host "[MODULAR CORE] Run restoration qualification"
python -m pytest -q .\tests\test_modular_core_restore.py
if ($LASTEXITCODE -ne 0) {
    throw "MODULAR CORE QUALIFICATION: FAIL"
}

Write-Host ""
Write-Host "MODULAR CORE QUALIFICATION: PASS"
