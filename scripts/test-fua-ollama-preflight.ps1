$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 OLLAMA REAL-MODEL PREFLIGHT ==="

$TempPy = Join-Path $env:TEMP "fua-ollama-preflight.py"

@'
import json
import time
import http.client

from father_fua.local_models import discover_local_models
from father_fua.real_model_runtime import RealModelMissionRuntime

def req(method, path, payload=None, timeout=300):
    conn=http.client.HTTPConnection("127.0.0.1",11434,timeout=timeout)
    try:
        body=None if payload is None else json.dumps(payload).encode("utf-8")
        headers={"Accept":"application/json"}
        if body is not None:
            headers["Content-Type"]="application/json"
        conn.request(method,path,body=body,headers=headers)
        resp=conn.getresponse()
        raw=resp.read().decode("utf-8")
        if resp.status < 200 or resp.status >= 300:
            raise RuntimeError("HTTP {} {}".format(resp.status,raw[:500]))
        return json.loads(raw)
    finally:
        conn.close()

models=discover_local_models()
print("DISCOVERED      : {}".format(len(models)))
if not models:
    raise SystemExit(20)

runtime=RealModelMissionRuntime(discoverer=lambda:models)
model=runtime.choose_model()
print("SELECTED MODEL  : {}".format(model.model_id))

try:
    ps=req("GET","/api/ps",timeout=10)
    running=[m.get("name") for m in ps.get("models",[])]
    print("ALREADY LOADED : {}".format(",".join(x for x in running if x) if running else "NONE"))
except Exception as e:
    print("API PS         : {}".format(e))

print("WARMUP          : START")
started=time.perf_counter()
data=req(
    "POST",
    "/api/generate",
    payload={
        "model":model.model_id,
        "prompt":"Reply with exactly: READY",
        "stream":False,
        "keep_alive":"10m",
        "options":{"num_predict":8,"temperature":0},
    },
    timeout=600,
)
elapsed=int((time.perf_counter()-started)*1000)
response=(data.get("response") or "").strip()
print("WARMUP MS       : {}".format(elapsed))
print("WARMUP RESPONSE : {}".format(response[:200]))
print("LOAD DURATION   : {}".format(data.get("load_duration")))
print("EVAL COUNT      : {}".format(data.get("eval_count")))
print("DONE            : {}".format(data.get("done")))

if not response:
    raise SystemExit(21)

print("")
print("OLLAMA REAL-MODEL PREFLIGHT RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "Ollama real-model preflight failed with exit code $Code"
}
