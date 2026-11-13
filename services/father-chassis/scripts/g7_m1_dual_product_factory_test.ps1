param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $serviceDir "..\..")).Path
$trustDir = Join-Path $repoRoot "projects\FATHER-TRUST-COMPETENCY-0001"
$artifactDir = Join-Path $serviceDir "artifacts"
$artifactPath = Join-Path $artifactDir "g7_m1_dual_product_factory_qualification_2026-11-13.json"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host "[G7 M1] $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result = [ordered]@{
    qualification = "G7_M1_DUAL_PRODUCT_FACTORY"
    started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    chassis_regression = $false
    trust_regression = $false
    dual_product_runtime = $false
    trust_ledger_verified = $false
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
        $result.chassis_regression = $true
    }
    finally {
        Pop-Location
    }

    Push-Location $trustDir
    try {
        Invoke-Step "Compile Trust & Competency sources/tests" {
            & $Python -m compileall -q src tests
        }

        Invoke-Step "Run Trust & Competency regression" {
            & $Python -m pytest -q
        }
        $result.trust_regression = $true
    }
    finally {
        Pop-Location
    }

    $env:PYTHONPATH = (
        (Join-Path $serviceDir "src") + [IO.Path]::PathSeparator +
        (Join-Path $trustDir "src")
    )
    $env:G7_M1_ARTIFACT = $artifactPath

    Invoke-Step "Assemble, execute and qualify OSINT + Security/KII products" {
@'
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from father.bootstrap import build_runtime
from father.core.approval import ApprovalRequired
from father.factory.product_runtime import AssembledProductRuntime
from father.factory.reference_products import osint_knowledge_spec, security_kii_spec
from trust_competency.ledger import EvidenceLedger
from trust_competency.models import EvidenceRecord

artifact_path = Path(os.environ["G7_M1_ARTIFACT"])

with tempfile.TemporaryDirectory(prefix="father-g7-m1-") as tmp:
    runtime = build_runtime(data_dir=tmp)
    runtime.rag.ingest(
        "qualification://osint",
        "OSINT analysis uses traceable sources, evidence, provenance and auditable reporting.",
    )
    runtime.rag.ingest(
        "qualification://kii",
        "KII security analysis requires policy enforcement, normative evidence and human validation.",
    )

    product_runtime = AssembledProductRuntime(runtime)

    osint_spec = osint_knowledge_spec()
    osint_product, osint_execution, osint_record = product_runtime.execute(
        spec=osint_spec,
        user_input="How does OSINT analysis use evidence and provenance?",
    )
    assert osint_record.qualified is True
    assert osint_execution.evidence

    kii_spec = security_kii_spec()
    approval_required = False
    pending_approval_id = None
    try:
        product_runtime.execute(
            spec=kii_spec,
            user_input="What does KII security analysis require?",
        )
    except ApprovalRequired as exc:
        approval_required = True
        pending_approval_id = exc.approval_id

    assert approval_required is True
    assert pending_approval_id

    approved = runtime.approval_gate.approve(pending_approval_id)
    kii_product, kii_execution, kii_record = product_runtime.execute(
        spec=kii_spec,
        user_input="What does KII security analysis require?",
        approval_id=approved.approval_id,
    )
    assert kii_record.qualified is True
    assert kii_execution.evidence

    assert osint_product.recipe.product_id != kii_product.recipe.product_id
    assert osint_product.recipe.recipe_hash != kii_product.recipe.recipe_hash
    assert osint_product.assembly.assembly_hash != kii_product.assembly.assembly_hash

    observed_at = datetime.now(timezone.utc).isoformat()
    ledger = EvidenceLedger()
    ledger.append(EvidenceRecord(
        evidence_id="EVD-G7-M1-OSINT",
        subject_id=osint_record.product_id,
        claim_id="CLM-G7-M1-RUNTIME-QUALIFIED",
        evidence_type="product_run_qualification",
        artifact_ref="runtime://osint",
        artifact_hash=osint_record.evidence_hash,
        observed_at=observed_at,
        issuer="FATHER G7 M1 qualification",
        metadata={
            "recipe_hash": osint_record.recipe_hash,
            "assembly_hash": osint_record.assembly_hash,
            "qualification_hash": osint_record.qualification_hash,
        },
    ))
    ledger.append(EvidenceRecord(
        evidence_id="EVD-G7-M1-KII",
        subject_id=kii_record.product_id,
        claim_id="CLM-G7-M1-RUNTIME-QUALIFIED",
        evidence_type="product_run_qualification",
        artifact_ref="runtime://security-kii",
        artifact_hash=kii_record.evidence_hash,
        observed_at=observed_at,
        issuer="FATHER G7 M1 qualification",
        metadata={
            "recipe_hash": kii_record.recipe_hash,
            "assembly_hash": kii_record.assembly_hash,
            "qualification_hash": kii_record.qualification_hash,
            "human_approval_verified": True,
        },
    ))
    assert ledger.verify() is True

    payload = {
        "qualification": "G7_M1_DUAL_PRODUCT_FACTORY",
        "passed": True,
        "same_chassis": True,
        "distinct_products": True,
        "human_approval_contract_verified": True,
        "trust_ledger_verified": True,
        "products": {
            "osint": {
                "product_id": osint_record.product_id,
                "version": osint_record.version,
                "recipe_hash": osint_record.recipe_hash,
                "assembly_hash": osint_record.assembly_hash,
                "trace_id": osint_record.trace_id,
                "qualification_id": osint_record.qualification_id,
                "qualification_hash": osint_record.qualification_hash,
                "evidence_hash": osint_record.evidence_hash,
                "qualified": osint_record.qualified,
            },
            "security_kii": {
                "product_id": kii_record.product_id,
                "version": kii_record.version,
                "recipe_hash": kii_record.recipe_hash,
                "assembly_hash": kii_record.assembly_hash,
                "trace_id": kii_record.trace_id,
                "qualification_id": kii_record.qualification_id,
                "qualification_hash": kii_record.qualification_hash,
                "evidence_hash": kii_record.evidence_hash,
                "qualified": kii_record.qualified,
                "approval_id": approved.approval_id,
            },
        },
        "trust_ledger_records": [
            {
                "evidence_id": item.evidence_id,
                "record_hash": item.record_hash,
                "parent_evidence_hash": item.parent_evidence_hash,
            }
            for item in ledger.records()
        ],
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
'@ | & $Python -
    }
    $result.dual_product_runtime = $true

    $runtimeResult = Get-Content -Path $artifactPath -Raw | ConvertFrom-Json
    if (-not $runtimeResult.trust_ledger_verified) {
        throw "Trust evidence ledger verification failed"
    }
    $result.trust_ledger_verified = $true

    $result.passed = (
        $result.chassis_regression -and
        $result.trust_regression -and
        $result.dual_product_runtime -and
        $result.trust_ledger_verified -and
        [bool]$runtimeResult.passed
    )
}
catch {
    $result.error = $_.Exception.Message
}
finally {
    $result.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
}

if (-not $result.passed) {
    Write-Host ""
    Write-Host "G7 M1 DUAL PRODUCT FACTORY: FAIL"
    $result | ConvertTo-Json -Depth 10
    exit 1
}

Write-Host ""
Write-Host "G7 M1 DUAL PRODUCT FACTORY: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Evidence: $artifactPath"
exit 0
