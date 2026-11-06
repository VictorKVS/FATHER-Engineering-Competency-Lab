$ErrorActionPreference = "Stop"

$Desired = "F:\FATHER_MODELS\ollama"
$Db = "$env:LOCALAPPDATA\Ollama\db.sqlite"
$BackupDir = "$env:LOCALAPPDATA\Ollama\fua-backups"
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (-not (Test-Path $Db)) { throw "Ollama settings DB not found: $Db" }
if (-not (Test-Path $Desired)) { throw "Desired model root not found: $Desired" }
if (-not (Test-Path $OllamaExe)) { throw "Ollama executable not found: $OllamaExe" }

Write-Host "=== FUA-001 OLLAMA WINDOWS SETTINGS REPAIR ==="
Write-Host "DESIRED MODEL LOCATION: $Desired"

Write-Host ""
Write-Host "01. Stop Ollama desktop/server processes"
Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^ollama$|^Ollama App$|^Ollama$' } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "02. Backup settings database"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Backup = Join-Path $BackupDir "db-$Stamp.sqlite"
Copy-Item $Db $Backup -Force
Write-Host "BACKUP       : $Backup"

Write-Host ""
Write-Host "03. Discover and update persisted model-location setting"
$Repo = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
$TempPy = Join-Path $env:TEMP "fua-ollama-db-repair.py"

@'
import os, sqlite3, sys

db=os.path.expandvars(r"%LOCALAPPDATA%\Ollama\db.sqlite")
desired=r"F:\FATHER_MODELS\ollama"

con=sqlite3.connect(db)
con.execute("pragma busy_timeout=5000")
updated=0
found=[]

try:
    tables=[r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    for table in tables:
        cols=[r[1] for r in con.execute("pragma table_info({})".format(table))]
        if not cols:
            continue

        rows=con.execute("select rowid,* from {}".format(table)).fetchall()
        for row in rows:
            rowid=row[0]
            vals=row[1:]
            for idx,val in enumerate(vals):
                if not isinstance(val,str):
                    continue
                low=val.lower()
                if "\\.ollama\\models" in low or low.endswith("\\ollama\\models") or low.endswith("/ollama/models"):
                    col=cols[idx]
                    found.append((table,rowid,col,val))
                    con.execute(
                        'update "{}" set "{}"=? where rowid=?'.format(table,col),
                        (desired,rowid),
                    )
                    updated += 1

    con.commit()

    print("CANDIDATES={}".format(len(found)))
    for item in found:
        print("UPDATED {} rowid={} column={} old={}".format(*item))
    print("UPDATED_COUNT={}".format(updated))

    if updated == 0:
        raise SystemExit(31)
finally:
    con.close()
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code = $LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -eq 31) {
    Write-Host "No persisted model-location row was found; restoring untouched DB."
    Copy-Item $Backup $Db -Force
    exit 31
}
if ($Code -ne 0) {
    Write-Host "DB update failed; restoring backup."
    Copy-Item $Backup $Db -Force
    throw "Ollama settings DB repair failed"
}

Write-Host ""
Write-Host "04. Persist matching user environment variable"
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS",$Desired,"User")
$env:OLLAMA_MODELS=$Desired
$env:OLLAMA_HOST="127.0.0.1:11434"

Write-Host ""
Write-Host "05. Start Ollama desktop executable/server"
$Proc = Start-Process -FilePath $OllamaExe -ArgumentList "serve" -PassThru -WindowStyle Hidden

$ready=$false
for($i=1;$i -le 40;$i++){
    Start-Sleep -Milliseconds 500
    try {
        $tags=Invoke-RestMethod "http://127.0.0.1:11434/api/tags"
        $ready=$true
        break
    } catch {}
}
if(-not $ready){
    Copy-Item $Backup $Db -Force
    throw "Ollama did not become ready after settings repair"
}

$count=@($tags.models).Count
Write-Host "API MODELS    : $count"
if($count -gt 0){
    $tags.models | Select-Object name,size,modified_at | Format-Table -AutoSize
}

if($count -eq 0){
    Write-Host ""
    Write-Host "SETTINGS REPAIR RESULT: BLOCKED - DB UPDATED BUT API STILL EMPTY"
    exit 32
}

Write-Host ""
Write-Host "06. FUA discovery"
$TempPy2 = Join-Path $env:TEMP "fua-after-settings-repair.py"
@'
from father_fua.local_models import discover_local_models
models=discover_local_models()
print("FUA_DISCOVERED={}".format(len(models)))
for m in models:
    print("{}|{}|{}".format(m.transport,m.model_id,m.base_url))
if not models:
    raise SystemExit(33)
'@ | Set-Content -Path $TempPy2 -Encoding UTF8

try {
    & $Py $TempPy2
    $Code2=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy2 -Force -ErrorAction SilentlyContinue
}
if($Code2 -ne 0){ throw "FUA discovery failed after Ollama settings repair" }

Write-Host ""
Write-Host "OLLAMA WINDOWS SETTINGS REPAIR RESULT: PASS"
