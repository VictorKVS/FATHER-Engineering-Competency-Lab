param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_m4_typed_stage_artifacts_qualification_2026-11-13.json"

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host "[G7 M4] $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result = [ordered]@{
    qualification = "G7_M4_TYPED_STAGE_ARTIFACTS"
    started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    toolchain_ready = $false
    regression = $false
    typed_roundtrip = $false
    wrong_type_rejected = $false
    unknown_version_rejected = $false
    persisted_typed_restore = $false
    tamper_detection = $false
    snapshot_schema_v2 = $false
    passed = $false
}

try {
    Push-Location $serviceDir
    try {
        Write-Host "[G7 M4] Verify qualification toolchain"
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
        $env:G7_M4_ARTIFACT = $artifactPath

        Invoke-Step "Verify typed artifact contracts and persistent round-trip" {
@'
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from father.core.state import SQLiteStateStore
from father.engineering.delivery_contract import (
    AcceptanceCriterion,
    AlgorithmSpec,
    ArchitectureSpec,
    BusinessProcessSpec,
    DevelopmentPacketBuilder,
    InterfaceContract,
    TestContract,
    VariableContract,
)
from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow, StageArtifact
from father.engineering.stage_artifacts import (
    CustomerRequestPayload,
    SystemAnalysisPackage,
    deserialize_stage_payload,
    serialize_stage_payload,
)

artifact_path = Path(os.environ["G7_M4_ARTIFACT"])

request = CustomerRequestPayload(
    request_id="REQ-G7-M4",
    title="Typed engineering handoff",
    objective="Eliminate untyped stage dictionaries",
)
request_raw = serialize_stage_payload("customer_request", 1, request)
request_restored = deserialize_stage_payload("customer_request", 1, request_raw)
assert request_restored == request
assert isinstance(request_restored, CustomerRequestPayload)

process = BusinessProcessSpec(
    process_id="BP-G7-M4",
    goal="typed handoff",
    inputs=("customer_request",),
    outputs=("business_process",),
    actors=("factory",),
    approved=True,
)
algorithm = AlgorithmSpec(
    algorithm_id="ALG-G7-M4",
    process_id=process.process_id,
    preconditions=("approved process",),
    steps=("validate", "handoff"),
    postconditions=("typed artifact",),
    approved=True,
)
variable = VariableContract(
    name="artifact",
    type_name="StageArtifact",
    owner_block="EngineeringWorkflow",
    direction="input",
)
interface = InterfaceContract(
    interface_id="IF-G7-M4",
    producer="EngineeringWorkflow",
    consumer="EngineeringWorkflow",
    request_schema=(variable,),
    response_schema=(),
)
architecture = ArchitectureSpec(
    architecture_id="ARCH-G7-M4",
    algorithm_id=algorithm.algorithm_id,
    blocks=("EngineeringWorkflow",),
    interfaces=(interface,),
    states=("READY",),
    approved=True,
)
test_contract = TestContract(
    test_contract_id="TEST-G7-M4",
    architecture_id=architecture.architecture_id,
    criteria=(
        AcceptanceCriterion(
            criterion_id="AC-G7-M4",
            statement="typed payload survives round trip",
            metric="typed_roundtrip",
            operator="==",
            threshold=1,
            evidence_type="qualification",
        ),
    ),
    approved=True,
)
packet = DevelopmentPacketBuilder.build(
    packet_id="DEV-G7-M4",
    business_process=process,
    algorithm=algorithm,
    architecture=architecture,
    test_contract=test_contract,
    system_analysis_approved=True,
)
packet_restored = deserialize_stage_payload(
    "DevelopmentPacket",
    1,
    serialize_stage_payload("DevelopmentPacket", 1, packet),
)
assert packet_restored == packet
assert isinstance(packet_restored.architecture, ArchitectureSpec)
assert isinstance(packet_restored.architecture.interfaces[0], InterfaceContract)
assert isinstance(packet_restored.architecture.interfaces[0].request_schema[0], VariableContract)
assert isinstance(packet_restored.test_contract, TestContract)

wrong_type_rejected = False
try:
    StageArtifact(
        artifact_id="BAD-DICT",
        artifact_type="customer_request",
        producer_agent_id="HUMAN_APPROVAL",
        payload={"request_id": "BAD"},
        approved=True,
    )
except TypeError:
    wrong_type_rejected = True
assert wrong_type_rejected

unknown_version_rejected = False
try:
    StageArtifact(
        artifact_id="BAD-VERSION",
        artifact_type="customer_request",
        producer_agent_id="HUMAN_APPROVAL",
        payload=request,
        approved=True,
        payload_schema_version=99,
    )
except ValueError:
    unknown_version_rejected = True
assert unknown_version_rejected

system_analysis = SystemAnalysisPackage(
    analysis_id="SYS-G7-M4",
    functional_requirements=("FR-1",),
    nonfunctional_requirements=("NFR-1",),
    states=("READY",),
    events=("START",),
    data_entities=("StageArtifact",),
    interfaces=("IF-G7-M4",),
    failure_modes=("schema_mismatch",),
    approved=True,
)

with tempfile.TemporaryDirectory(prefix="father-g7-m4-") as tmp:
    store = SQLiteStateStore(Path(tmp) / "workflow.db")
    first = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M4")
    first.add_external_artifact(
        StageArtifact(
            artifact_id="REQ-G7-M4",
            artifact_type="customer_request",
            producer_agent_id="HUMAN_APPROVAL",
            payload=request,
            approved=True,
        )
    )
    first.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        StageArtifact(
            artifact_id="BP-G7-M4",
            artifact_type="BusinessProcessSpec",
            producer_agent_id="FTH-AGENT-BUSINESS-ANALYST",
            payload=process,
            approved=True,
        ),
    )
    first.submit_stage_artifact(
        "SYSTEM_ANALYSIS",
        StageArtifact(
            artifact_id="SYS-G7-M4",
            artifact_type="SystemAnalysisPackage",
            producer_agent_id="FTH-AGENT-SYSTEM-ANALYST",
            payload=system_analysis,
            approved=True,
        ),
    )

    snapshot = store.get(FactoryEngineeringWorkflow.NAMESPACE, "WF-G7-M4")
    assert snapshot["schema_version"] == 2
    assert snapshot["artifacts"]["customer_request"]["payload_schema_version"] == 1
    assert "payload_data" in snapshot["artifacts"]["customer_request"]

    second = FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M4")
    restored_request = second._artifacts["customer_request"].payload
    restored_system = second._artifacts["SystemAnalysisPackage"].payload
    assert isinstance(restored_request, CustomerRequestPayload)
    assert isinstance(restored_system, SystemAnalysisPackage)
    assert restored_request == request
    assert restored_system == system_analysis
    assert second.available_stage().stage_id == "ALGORITHM_SELECTION"

    tampered = store.get(FactoryEngineeringWorkflow.NAMESPACE, "WF-G7-M4")
    tampered["artifacts"]["customer_request"]["payload_data"]["objective"] = "forged"
    store.set(FactoryEngineeringWorkflow.NAMESPACE, "WF-G7-M4", tampered)

    tamper_detected = False
    try:
        FactoryEngineeringWorkflow(store=store, workflow_id="WF-G7-M4")
    except ValueError as exc:
        tamper_detected = "stage artifact hash mismatch" in str(exc)
    assert tamper_detected

payload = {
    "qualification": "G7_M4_TYPED_STAGE_ARTIFACTS",
    "passed": True,
    "typed_roundtrip": True,
    "wrong_type_rejected": wrong_type_rejected,
    "unknown_version_rejected": unknown_version_rejected,
    "persisted_typed_restore": True,
    "tamper_detection": True,
    "snapshot_schema_v2": True,
    "development_packet_nested_types_preserved": True,
    "next_stage_after_restore": "ALGORITHM_SELECTION",
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
        $result.typed_roundtrip = [bool]$runtimeResult.typed_roundtrip
        $result.wrong_type_rejected = [bool]$runtimeResult.wrong_type_rejected
        $result.unknown_version_rejected = [bool]$runtimeResult.unknown_version_rejected
        $result.persisted_typed_restore = [bool]$runtimeResult.persisted_typed_restore
        $result.tamper_detection = [bool]$runtimeResult.tamper_detection
        $result.snapshot_schema_v2 = [bool]$runtimeResult.snapshot_schema_v2
        $result.passed = (
            $result.toolchain_ready -and
            $result.regression -and
            $result.typed_roundtrip -and
            $result.wrong_type_rejected -and
            $result.unknown_version_rejected -and
            $result.persisted_typed_restore -and
            $result.tamper_detection -and
            $result.snapshot_schema_v2 -and
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
        Write-Host "G7 M4 TYPED STAGE ARTIFACTS: ENVIRONMENT BLOCKED"
    }
    else {
        Write-Host "G7 M4 TYPED STAGE ARTIFACTS: FAIL"
    }
    $result | ConvertTo-Json -Depth 10
    exit 1
}

Write-Host ""
Write-Host "G7 M4 TYPED STAGE ARTIFACTS: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Evidence: $artifactPath"
exit 0
