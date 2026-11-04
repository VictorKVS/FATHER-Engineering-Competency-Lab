$ErrorActionPreference="Stop"
Write-Host "=== FATHER STORY AGENT MVP-01 ===" -ForegroundColor Cyan
python --version
python -m compileall story_studio_server.py run_story_agent_mvp01.py
if ($LASTEXITCODE -ne 0) { throw "Story Agent syntax check failed" }
python .\run_story_agent_mvp01.py
if ($LASTEXITCODE -ne 0) { throw "Story Agent MVP-01 failed" }
Write-Host "=== FATHER STORY AGENT MVP-01: PASS ===" -ForegroundColor Green
Write-Host "Start: .\START_FATHER_STORY_STUDIO.ps1" -ForegroundColor Yellow
