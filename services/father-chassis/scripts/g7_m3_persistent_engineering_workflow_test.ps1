param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_m3_persistent_engineering_workflow_qualification_2026-11-13.json"

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host "[G7 M3] $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result = [ordered]@{
    qualification = "G7_M3_PERSISTENT_ENGINEERING_WORKFLOW"
    started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    toolchain_ready = $false
    regression = $false
    restart_restore = $false
    stage_authority_preserved = $false
    workflow_isolation = $false
    tamper_detection = $false
    blocked_history_preserved = $false
    passed = $false
}

try {
    Push-Location $serviceDir
    try {
        Write-Host "[G7 M3] Verify qualification toolchain"
        & $Python -m ruff --version *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff is not installed. Run: $Python -m pip install -e '.[dev]'"
        }
        & $Python -m pytest --version *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "QUALIFICATION_ENVIRONMENT_BLOCKED: pytest is not installed. Run: $Python -m pip install -e '.[dev]'"
        }
        $result.toolchain_ready = $true

        Invoke-Step "Compile father-chassis sources/tests" {
            & $Python -m compileall -q src tests
        }

        Invoke-Step "Static undefined-name gate" {
            & $Python -m ruff check src tests --select F821,F822,F823
        }

        Invoke-Step "Run full father-chassis regression" {
            & $Python -m pytest -q
        }
        $result.regression = $true

        $env:PYTHONPATH = (Join-Path $serviceDir "src")
        $env:G7_M3_ARTIFACT = $artifactPath

        Invoke-Step "Verify persistent engineering governance across restart" {
@'
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from father.core.state import SQLiteStateStore
from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow, StageArtifact

artifact_path = Path(os.environ["G7_M3_ARTIFACT"])

def artifact(artifact_id, artifact_type, producer, approved=True):
    return StageArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        producer_agent_id=producer,
        payload={"artifact_type": artifact_type, "qualification": "G7_M3"},
        approved=approved,
        evidence_refs=(f"evidence://{artifact_id}",),
    )

with tempfile.TemporaryDirectory(prefix="father-g7-m3-") as tmp:
    store = SQLiteStateStore(Path(tmp) / "workflow.db")

    first = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M3")
    first.add_external_artifact(
        artifact("REQ-G7-M3", "customer_request", "HUMAN_APPROVAL")
    )
    assert first.available_stage().stage_id == "BUSINESS_ANALYSIS"

    first.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        artifact(
            "BP-G7-M3",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )
    first.submit_stage_artifact(
        "SYSTEM_ANALYSIS",
        artifact(
            "SYS-G7-M3",
            "SystemAnalysisPackage",
            "FTH-AGENT-SYSTEM-ANALYST",
        ),
    )
    before_restart_next = first.available_stage().stage_id
    before_restart_hash = first.workflow_hash()

    second = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M3")
    after_restart_next = second.available_stage().stage_id
    assert before_restart_next == "ALGORITHM_SELECTION"
    assert after_restart_next == before_restart_next
    assert second.status()["completed_stages"] == [
        "BUSINESS_ANALYSIS",
        "SYSTEM_ANALYSIS",
    ]

    isolated = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M3-OTHER")
    assert isolated.available_stage() is None
    assert isolated.status()["artifacts"] == {}

    blocked = second.submit_stage_artifact(
        "ALGORITHM_SELECTION",
        artifact(
            "ALG-WRONG",
            "AlgorithmSpec",
            "FTH-AGENT-SENIOR-DEVELOPER",
        ),
    )
    assert blocked.status == "BLOCKED"

    third = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M3")
    assert third.available_stage().stage_id == "ALGORITHM_SELECTION"
    assert third.status()["history"][-1]["status"] == "BLOCKED"

    tamper_store = SQLiteStateStore(Path(tmp) / "tamper.db")
    tamper = FactoryEngineeringWorkflow(store=tamper_store, workflow_id="WF-TAMPER")
    tamper.add_external_artifact(
        artifact("REQ-TAMPER", "customer_request", "HUMAN_APPROVAL")
    )
    snapshot = tamper_store.get(FactoryEngineeringWorkflow.NAMESPACE, "WF-TAMPER")
    snapshot["artifacts"]["customer_request"]["payload"]["artifact_type"] = "forged"
    tamper_store.set(FactoryEngineeringWorkflow.NAMESPACE, "WF-TAMPER", snapshot)

    tamper_detected = False
    try:
        FactoryEngineeringWorkflow(store=tamper_store, workflow_id="WF-TAMPER")
    except ValueError as exc:
        tamper_detected = "stage artifact hash mismatch" in str(exc)
    assert tamper_detected

    payload = {
        "qualification": "G7_M3_PERSISTENT_ENGINEERING_WORKFLOW",
        "passed": True,
        "restart_restore": True,
        "stage_authority_preserved": True,
        "workflow_isolation": True,
        "tamper_detection": True,
        "blocked_history_preserved": True,
        "workflow_id": "WF-G7-M3",
        "next_stage_before_restart": before_restart_next,
        "next_stage_after_restart": after_restart_next,
        "workflow_hash_before_restart": before_restart_hash,
        "workflow_hash_after_restore": second.workflow_hash(),
        "completed_stages_after_restore": second.status()["completed_stages"],
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
        $result.restart_restore = [bool]$runtimeResult.restart_restore
        $result.stage_authority_preserved = [bool]$runtimeResult.stage_authority_preserved
        $result.workflow_isolation = [bool]$runtimeResult.workflow_isolation
        $result.tamper_detection = [bool]$runtimeResult.tamper_detection
        $result.blocked_history_preserved = [bool]$runtimeResult.blocked_history_preserved
        $result.passed = (
            $result.regression -and
            $result.restart_restore -and
            $result.stage_authority_preserved -and
            $result.workflow_isolation -and
            $result.tamper_detection -and
            $result.blocked_history_preserved -and
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
    if (($result.error -as [string]) -like "QUALIFICATION_ENVIRONMENT_BLOCKED:*") {
        Write-Host "G7 M3 PERSISTENT ENGINEERING WORKFLOW: ENVIRONMENT BLOCKED"
    }
    else {
        Write-Host "G7 M3 PERSISTENT ENGINEERING WORKFLOW: FAIL"
    }
    $result | ConvertTo-Json -Depth 10
    exit 1
}

Write-Host ""
Write-Host "G7 M3 PERSISTENT ENGINEERING WORKFLOW: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Evidence: $artifactPath"
exit 0
