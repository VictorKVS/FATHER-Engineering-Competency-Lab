from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from father.engineering.delivery_contract import (
    AcceptanceCriterion,
    AlgorithmSpec,
    ArchitectureSpec,
    BusinessProcessSpec,
    DevelopmentPacket,
    InterfaceContract,
    TestContract,
    VariableContract,
)


@dataclass(frozen=True, slots=True)
class CustomerRequestPayload:
    request_id: str
    title: str
    objective: str


@dataclass(frozen=True, slots=True)
class SystemAnalysisPackage:
    analysis_id: str
    functional_requirements: tuple[str, ...]
    nonfunctional_requirements: tuple[str, ...]
    states: tuple[str, ...]
    events: tuple[str, ...]
    data_entities: tuple[str, ...]
    interfaces: tuple[str, ...]
    failure_modes: tuple[str, ...]
    approved: bool = False


@dataclass(frozen=True, slots=True)
class ImplementationChange:
    change_id: str
    changed_files: tuple[str, ...]
    traceability_refs: tuple[str, ...]
    tests: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeliveryQualification:
    delivery_id: str
    build_ref: str
    deployment_ref: str
    security_evidence: tuple[str, ...]
    observability_evidence: tuple[str, ...]
    rollback_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QualificationDecision:
    qualification_id: str
    status: str
    criteria_results: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    blocking_findings: tuple[str, ...] = ()


StagePayload = (
    CustomerRequestPayload
    | BusinessProcessSpec
    | SystemAnalysisPackage
    | AlgorithmSpec
    | ArchitectureSpec
    | TestContract
    | DevelopmentPacket
    | ImplementationChange
    | DeliveryQualification
    | QualificationDecision
)


@dataclass(frozen=True, slots=True)
class ArtifactSchema:
    artifact_type: str
    schema_version: int
    payload_type: type
    serializer: Callable[[Any], dict[str, Any]]
    deserializer: Callable[[dict[str, Any]], Any]


def _business_from_dict(raw: dict[str, Any]) -> BusinessProcessSpec:
    return BusinessProcessSpec(
        process_id=str(raw["process_id"]),
        goal=str(raw["goal"]),
        inputs=tuple(str(x) for x in raw["inputs"]),
        outputs=tuple(str(x) for x in raw["outputs"]),
        actors=tuple(str(x) for x in raw["actors"]),
        success_metrics={str(k): float(v) for k, v in raw.get("success_metrics", {}).items()},
        approved=bool(raw.get("approved", False)),
    )


def _algorithm_from_dict(raw: dict[str, Any]) -> AlgorithmSpec:
    return AlgorithmSpec(
        algorithm_id=str(raw["algorithm_id"]),
        process_id=str(raw["process_id"]),
        preconditions=tuple(str(x) for x in raw["preconditions"]),
        steps=tuple(str(x) for x in raw["steps"]),
        postconditions=tuple(str(x) for x in raw["postconditions"]),
        invariants=tuple(str(x) for x in raw.get("invariants", ())),
        complexity_limits={str(k): float(v) for k, v in raw.get("complexity_limits", {}).items()},
        approved=bool(raw.get("approved", False)),
    )


def _variable_from_dict(raw: dict[str, Any]) -> VariableContract:
    return VariableContract(
        name=str(raw["name"]),
        type_name=str(raw["type_name"]),
        owner_block=str(raw["owner_block"]),
        direction=str(raw["direction"]),
        required=bool(raw.get("required", True)),
        nullable=bool(raw.get("nullable", False)),
        description=str(raw.get("description", "")),
    )


def _interface_from_dict(raw: dict[str, Any]) -> InterfaceContract:
    latency = raw.get("latency_slo_ms")
    return InterfaceContract(
        interface_id=str(raw["interface_id"]),
        producer=str(raw["producer"]),
        consumer=str(raw["consumer"]),
        request_schema=tuple(_variable_from_dict(dict(x)) for x in raw["request_schema"]),
        response_schema=tuple(_variable_from_dict(dict(x)) for x in raw["response_schema"]),
        errors=tuple(str(x) for x in raw.get("errors", ())),
        latency_slo_ms=None if latency is None else float(latency),
    )


def _architecture_from_dict(raw: dict[str, Any]) -> ArchitectureSpec:
    return ArchitectureSpec(
        architecture_id=str(raw["architecture_id"]),
        algorithm_id=str(raw["algorithm_id"]),
        blocks=tuple(str(x) for x in raw["blocks"]),
        interfaces=tuple(_interface_from_dict(dict(x)) for x in raw["interfaces"]),
        states=tuple(str(x) for x in raw["states"]),
        constants={str(k): str(v) for k, v in raw.get("constants", {}).items()},
        approved=bool(raw.get("approved", False)),
    )


def _criterion_from_dict(raw: dict[str, Any]) -> AcceptanceCriterion:
    threshold = raw["threshold"]
    if not isinstance(threshold, (int, float, str)):
        raise ValueError("invalid acceptance threshold type")
    return AcceptanceCriterion(
        criterion_id=str(raw["criterion_id"]),
        statement=str(raw["statement"]),
        metric=str(raw["metric"]),
        operator=str(raw["operator"]),
        threshold=threshold,
        evidence_type=str(raw["evidence_type"]),
    )


def _test_contract_from_dict(raw: dict[str, Any]) -> TestContract:
    return TestContract(
        test_contract_id=str(raw["test_contract_id"]),
        architecture_id=str(raw["architecture_id"]),
        criteria=tuple(_criterion_from_dict(dict(x)) for x in raw["criteria"]),
        required_test_levels=tuple(str(x) for x in raw.get("required_test_levels", ())),
        approved=bool(raw.get("approved", False)),
    )


def _development_packet_from_dict(raw: dict[str, Any]) -> DevelopmentPacket:
    return DevelopmentPacket(
        packet_id=str(raw["packet_id"]),
        business_process=_business_from_dict(dict(raw["business_process"])),
        algorithm=_algorithm_from_dict(dict(raw["algorithm"])),
        architecture=_architecture_from_dict(dict(raw["architecture"])),
        test_contract=_test_contract_from_dict(dict(raw["test_contract"])),
        system_analysis_approved=bool(raw["system_analysis_approved"]),
        packet_hash=str(raw["packet_hash"]),
    )


def _customer_request_from_dict(raw: dict[str, Any]) -> CustomerRequestPayload:
    return CustomerRequestPayload(
        request_id=str(raw["request_id"]),
        title=str(raw["title"]),
        objective=str(raw["objective"]),
    )


def _system_analysis_from_dict(raw: dict[str, Any]) -> SystemAnalysisPackage:
    return SystemAnalysisPackage(
        analysis_id=str(raw["analysis_id"]),
        functional_requirements=tuple(str(x) for x in raw["functional_requirements"]),
        nonfunctional_requirements=tuple(str(x) for x in raw["nonfunctional_requirements"]),
        states=tuple(str(x) for x in raw["states"]),
        events=tuple(str(x) for x in raw["events"]),
        data_entities=tuple(str(x) for x in raw["data_entities"]),
        interfaces=tuple(str(x) for x in raw["interfaces"]),
        failure_modes=tuple(str(x) for x in raw["failure_modes"]),
        approved=bool(raw.get("approved", False)),
    )


def _implementation_change_from_dict(raw: dict[str, Any]) -> ImplementationChange:
    return ImplementationChange(
        change_id=str(raw["change_id"]),
        changed_files=tuple(str(x) for x in raw["changed_files"]),
        traceability_refs=tuple(str(x) for x in raw["traceability_refs"]),
        tests=tuple(str(x) for x in raw["tests"]),
    )


def _delivery_qualification_from_dict(raw: dict[str, Any]) -> DeliveryQualification:
    return DeliveryQualification(
        delivery_id=str(raw["delivery_id"]),
        build_ref=str(raw["build_ref"]),
        deployment_ref=str(raw["deployment_ref"]),
        security_evidence=tuple(str(x) for x in raw["security_evidence"]),
        observability_evidence=tuple(str(x) for x in raw["observability_evidence"]),
        rollback_evidence=tuple(str(x) for x in raw["rollback_evidence"]),
    )


def _qualification_decision_from_dict(raw: dict[str, Any]) -> QualificationDecision:
    return QualificationDecision(
        qualification_id=str(raw["qualification_id"]),
        status=str(raw["status"]),
        criteria_results=tuple(str(x) for x in raw["criteria_results"]),
        evidence_refs=tuple(str(x) for x in raw["evidence_refs"]),
        blocking_findings=tuple(str(x) for x in raw.get("blocking_findings", ())),
    )


def _asdict(payload: Any) -> dict[str, Any]:
    value = asdict(payload)
    if not isinstance(value, dict):
        raise TypeError("artifact payload must serialize to a dict")
    return value


_SCHEMAS: dict[tuple[str, int], ArtifactSchema] = {
    ("customer_request", 1): ArtifactSchema("customer_request", 1, CustomerRequestPayload, _asdict, _customer_request_from_dict),
    ("BusinessProcessSpec", 1): ArtifactSchema("BusinessProcessSpec", 1, BusinessProcessSpec, _asdict, _business_from_dict),
    ("SystemAnalysisPackage", 1): ArtifactSchema("SystemAnalysisPackage", 1, SystemAnalysisPackage, _asdict, _system_analysis_from_dict),
    ("AlgorithmSpec", 1): ArtifactSchema("AlgorithmSpec", 1, AlgorithmSpec, _asdict, _algorithm_from_dict),
    ("ArchitectureSpec", 1): ArtifactSchema("ArchitectureSpec", 1, ArchitectureSpec, _asdict, _architecture_from_dict),
    ("TestContract", 1): ArtifactSchema("TestContract", 1, TestContract, _asdict, _test_contract_from_dict),
    ("DevelopmentPacket", 1): ArtifactSchema("DevelopmentPacket", 1, DevelopmentPacket, _asdict, _development_packet_from_dict),
    ("ImplementationChange", 1): ArtifactSchema("ImplementationChange", 1, ImplementationChange, _asdict, _implementation_change_from_dict),
    ("DeliveryQualification", 1): ArtifactSchema("DeliveryQualification", 1, DeliveryQualification, _asdict, _delivery_qualification_from_dict),
    ("QualificationDecision", 1): ArtifactSchema("QualificationDecision", 1, QualificationDecision, _asdict, _qualification_decision_from_dict),
}


def get_artifact_schema(artifact_type: str, schema_version: int = 1) -> ArtifactSchema:
    try:
        return _SCHEMAS[(artifact_type, schema_version)]
    except KeyError as exc:
        raise ValueError(
            f"unsupported artifact schema: {artifact_type}@v{schema_version}"
        ) from exc


def serialize_stage_payload(
    artifact_type: str,
    schema_version: int,
    payload: StagePayload,
) -> dict[str, Any]:
    schema = get_artifact_schema(artifact_type, schema_version)
    if not isinstance(payload, schema.payload_type):
        raise TypeError(
            f"artifact {artifact_type}@v{schema_version} requires "
            f"{schema.payload_type.__name__}, got {type(payload).__name__}"
        )
    return schema.serializer(payload)


def deserialize_stage_payload(
    artifact_type: str,
    schema_version: int,
    payload_data: dict[str, Any],
) -> StagePayload:
    schema = get_artifact_schema(artifact_type, schema_version)
    try:
        payload = schema.deserializer(payload_data)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            f"malformed payload for {artifact_type}@v{schema_version}"
        ) from exc
    if not isinstance(payload, schema.payload_type):
        raise TypeError("artifact deserializer returned wrong payload type")
    return payload
