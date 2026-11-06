$ErrorActionPreference = "Stop"

$Db = "$env:LOCALAPPDATA\Ollama\db.sqlite"
$Log = "$env:LOCALAPPDATA\Ollama\server.log"

Write-Host "=== FUA-001 OLLAMA WINDOWS SETTINGS INSPECT ==="

Write-Host ""
Write-Host "01. Port owner"
$listener = Get-NetTCPConnection -State Listen -LocalPort 11434 -ErrorAction SilentlyContinue
if ($listener) {
    $pids = @($listener | Select-Object -ExpandProperty OwningProcess -Unique)
    foreach ($pidValue in $pids) {
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue" -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "PID          : $pidValue"
            Write-Host "NAME         : $($proc.Name)"
            Write-Host "COMMAND LINE : $($proc.CommandLine)"
        }
    }
} else {
    Write-Host "PORT 11434   : CLOSED"
}

Write-Host ""
Write-Host "02. Environment"
Write-Host "OLLAMA_MODELS (process shell): $env:OLLAMA_MODELS"
Write-Host "OLLAMA_MODELS (user)         : $([Environment]::GetEnvironmentVariable('OLLAMA_MODELS','User'))"
Write-Host "OLLAMA_MODELS (machine)      : $([Environment]::GetEnvironmentVariable('OLLAMA_MODELS','Machine'))"

Write-Host ""
Write-Host "03. Desktop settings database"
if (Test-Path $Db) {
    Write-Host "DB           : $Db"
    $Py = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"
    $TempPy = Join-Path $env:TEMP "fua-ollama-db-inspect.py"

@'
import os, sqlite3, json
db=os.path.expandvars(r"%LOCALAPPDATA%\Ollama\db.sqlite")
con=sqlite3.connect("file:{}?mode=ro".format(db.replace("\\","/")), uri=True)
try:
    tables=[r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    print("TABLES={}".format(",".join(tables)))
    for table in tables:
        try:
            cols=[r[1] for r in con.execute("pragma table_info({})".format(table))]
            print("TABLE {} COLUMNS {}".format(table, cols))
            rows=con.execute("select * from {} limit 50".format(table)).fetchall()
            for row in rows:
                text=" | ".join("" if v is None else str(v) for v in row)
                if "model" in text.lower() or "setting" in table.lower() or "path" in text.lower():
                    print("ROW {} :: {}".format(table, text))
        except Exception as e:
            print("TABLE_ERROR {} {}".format(table,e))
finally:
    con.close()
'@ | Set-Content -Path $TempPy -Encoding UTF8

    try {
        & $Py $TempPy
        if ($LASTEXITCODE -ne 0) { throw "SQLite inspection failed" }
    }
    finally {
        Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "DB           : NOT FOUND"
}

Write-Host ""
Write-Host "04. Server log tail"
if (Test-Path $Log) {
    Get-Content $Log -Tail 120 | Select-String -Pattern "OLLAMA_MODELS|server config|models|cache hydration|error|warn" -CaseSensitive:$false
} else {
    Write-Host "SERVER LOG   : NOT FOUND"
}

Write-Host ""
Write-Host "OLLAMA WINDOWS SETTINGS INSPECT RESULT: COMPLETE"
