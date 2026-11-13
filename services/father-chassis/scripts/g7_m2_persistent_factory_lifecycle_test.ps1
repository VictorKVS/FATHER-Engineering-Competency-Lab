param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts"
$artifactPath = Join-Path $artifactDir "g7_m2_persistent_factory_lifecycle_qualification_2026-11-13.json"

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host "[G7 M2] $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result = [ordered]@{
    qualification = "G7_M2_PERSISTENT_FACTORY_LIFECYCLE"
    started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    regression = $false
    product_registry_restart = $false
    approval_restart = $false
    post_restart_execution = $false
    passed = $false
}

try {
    Push-Location $serviceDir
    try {
        Invoke-Step "Compile father-chassis sources/tests" {
            & $Python -m compileall -q src tests
        }

        Invoke-Step "Run full father-chassis regression" {
            & $Python -m pytest -q
        }
        $result.regression = $true

        $env:PYTHONPATH = (Join-Path $serviceDir "src")
        $env:G7_M2_ARTIFACT = $artifactPath

        Invoke-Step "Verify persistent product + approval lifecycle across runtime restarts" {
@'
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from father.bootstrap import build_runtime
from father.core.approval import ApprovalRequired
from father.factory.product_runtime import AssembledProductRuntime
from father.factory.reference_products import security_kii_spec

artifact_path = Path(os.environ["G7_M2_ARTIFACT"])

with tempfile.TemporaryDirectory(prefix="father-g7-m2-") as tmp:
    spec = security_kii_spec()

    runtime1 = build_runtime(data_dir=tmp)
    runtime1.rag.ingest(
        "qualification://kii-persistent",
        "KII security analysis requires policy enforcement, evidence and human approval.",
    )
    product_runtime1 = AssembledProductRuntime(runtime1)
    product1 = product_runtime1.compose(spec)
    recipe_hash = product1.recipe.recipe_hash
    assembly_hash = product1.assembly.assembly_hash

    pending_id = None
    try:
        product_runtime1.execute(
            spec=spec,
            user_input="What does KII security analysis require?",
        )
    except ApprovalRequired as exc:
        pending_id = exc.approval_id

    assert pending_id

    runtime2 = build_runtime(data_dir=tmp)
    product_runtime2 = AssembledProductRuntime(runtime2)
    restored = product_runtime2.registry.get(spec.product_id, spec.version)
    assert restored.recipe_hash == recipe_hash

    pending = runtime2.approval_gate.get(pending_id)
    assert pending.status == "pending"
    approved = runtime2.approval_gate.approve(pending_id)
    assert approved.status == "approved"

    runtime3 = build_runtime(data_dir=tmp)
    product_runtime3 = AssembledProductRuntime(runtime3)
    restored2 = product_runtime3.registry.get(spec.product_id, spec.version)
    approval = runtime3.approval_gate.get(pending_id)

    assert restored2.recipe_hash == recipe_hash
    assert approval.status == "approved"

    product3, execution3, record3 = product_runtime3.execute(
        spec=spec,
        user_input="What does KII security analysis require?",
        approval_id=pending_id,
    )

    assert execution3.status == "EXECUTED"
    assert execution3.qualification["qualified"] is True
    assert record3.qualified is True
    assert product3.recipe.recipe_hash == recipe_hash
    assert product3.assembly.assembly_hash == assembly_hash

    payload = {
        "qualification": "G7_M2_PERSISTENT_FACTORY_LIFECYCLE",
        "passed": True,
        "product_registry_restart": True,
        "approval_restart": True,
        "post_restart_execution": True,
        "product_id": spec.product_id,
        "version": spec.version,
        "recipe_hash": recipe_hash,
        "assembly_hash": assembly_hash,
        "approval_id": pending_id,
        "final_approval_status": approval.status,
        "trace_id": record3.trace_id,
        "qualification_id": record3.qualification_id,
        "qualification_hash": record3.qualification_hash,
        "evidence_hash": record3.evidence_hash,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
'@ | & $Python -
        }

        $runtimeResult = Get-Content -Path $artifactPath -Raw | ConvertFrom-Json
        $result.product_registry_restart = [bool]$runtimeResult.product_registry_restart
        $result.approval_restart = [bool]$runtimeResult.approval_restart
        $result.post_restart_execution = [bool]$runtimeResult.post_restart_execution

        $result.passed = (
            $result.regression -and
            $result.product_registry_restart -and
            $result.approval_restart -and
            $result.post_restart_execution -and
            [bool]$runtimeResult.passed
        )
    }
    finally {
        Pop-Location
    }
}
catch {
    $result.error = $_.Exception.Message
}
finally {
    $result.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
}

if (-not $result.passed) {
    Write-Host ""
    Write-Host "G7 M2 PERSISTENT FACTORY LIFECYCLE: FAIL"
    $result | ConvertTo-Json -Depth 10
    exit 1
}

Write-Host ""
Write-Host "G7 M2 PERSISTENT FACTORY LIFECYCLE: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Evidence: $artifactPath"
exit 0
