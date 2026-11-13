from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class BusinessProcessSpec:
    process_id: str
    goal: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    actors: tuple[str, ...]
    success_metrics: dict[str, float] = field(default_factory=dict)
    approved: bool = False


@dataclass(frozen=True, slots=True)
class AlgorithmSpec:
    algorithm_id: str
    process_id: str
    preconditions: tuple[str, ...]
    steps: tuple[str, ...]
    postconditions: tuple[str, ...]
    invariants: tuple[str, ...] = ()
    complexity_limits: dict[str, float] = field(default_factory=dict)
    approved: bool = False


@dataclass(frozen=True, slots=True)
class VariableContract:
    name: str
    type_name: str
    owner_block: str
    direction: str
    required: bool = True
    nullable: bool = False
    description: str = ""


@dataclass(frozen=True, slots=True)
class InterfaceContract:
    interface_id: str
    producer: str
    consumer: str
    request_schema: tuple[VariableContract, ...]
    response_schema: tuple[VariableContract, ...]
    errors: tuple[str, ...] = ()
    latency_slo_ms: float | None = None


@dataclass(frozen=True, slots=True)
class ArchitectureSpec:
    architecture_id: str
    algorithm_id: str
    blocks: tuple[str, ...]
    interfaces: tuple[InterfaceContract, ...]
    states: tuple[str, ...]
    constants: dict[str, str] = field(default_factory=dict)
    approved: bool = False


@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    criterion_id: str
    statement: str
    metric: str
    operator: str
    threshold: float | str
    evidence_type: str


@dataclass(frozen=True, slots=True)
class TestContract:
    test_contract_id: str
    architecture_id: str
    criteria: tuple[AcceptanceCriterion, ...]
    required_test_levels: tuple[str, ...] = (
        "static",
        "unit",
        "integration",
        "contract",
        "regression",
    )
    approved: bool = False


@dataclass(frozen=True, slots=True)
class DevelopmentPacket:
    packet_id: str
    business_process: BusinessProcessSpec
    algorithm: AlgorithmSpec
    architecture: ArchitectureSpec
    test_contract: TestContract
    system_analysis_approved: bool
    packet_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DevelopmentPacketBuilder:
    """Fail-closed pre-code gate for FATHER engineering work."""

    @staticmethod
    def build(
        *,
        packet_id: str,
        business_process: BusinessProcessSpec,
        algorithm: AlgorithmSpec,
        architecture: ArchitectureSpec,
        test_contract: TestContract,
        system_analysis_approved: bool,
    ) -> DevelopmentPacket:
        errors: list[str] = []

        if not business_process.approved:
            errors.append("business process is not approved")
        if not algorithm.approved:
            errors.append("algorithm is not approved")
        if not architecture.approved:
            errors.append("architecture is not approved")
        if not test_contract.approved:
            errors.append("test contract is not approved")
        if not system_analysis_approved:
            errors.append("system analysis is not approved")

        if algorithm.process_id != business_process.process_id:
            errors.append("algorithm.process_id does not match business process")
        if architecture.algorithm_id != algorithm.algorithm_id:
            errors.append("architecture.algorithm_id does not match algorithm")
        if test_contract.architecture_id != architecture.architecture_id:
            errors.append("test contract architecture_id does not match architecture")

        if not business_process.goal.strip():
            errors.append("business goal is required")
        if not business_process.inputs:
            errors.append("business process inputs are required")
        if not business_process.outputs:
            errors.append("business process outputs are required")
        if not algorithm.steps:
            errors.append("algorithm steps are required")
        if not architecture.blocks:
            errors.append("architecture blocks are required")
        if not architecture.interfaces:
            errors.append("architecture interfaces are required")
        if not test_contract.criteria:
            errors.append("acceptance criteria are required")

        declared_variables: set[str] = set()
        for interface in architecture.interfaces:
            if interface.producer not in architecture.blocks:
                errors.append(f"unknown interface producer: {interface.producer}")
            if interface.consumer not in architecture.blocks:
                errors.append(f"unknown interface consumer: {interface.consumer}")
            for variable in (*interface.request_schema, *interface.response_schema):
                if not variable.name.strip():
                    errors.append(f"empty variable name in {interface.interface_id}")
                if variable.owner_block not in architecture.blocks:
                    errors.append(
                        f"variable {variable.name} owner block is unknown: {variable.owner_block}"
                    )
                key = f"{interface.interface_id}:{variable.direction}:{variable.name}"
                if key in declared_variables:
                    errors.append(f"duplicate variable contract: {key}")
                declared_variables.add(key)

        criterion_ids = [item.criterion_id for item in test_contract.criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            errors.append("duplicate acceptance criterion id")

        if errors:
            raise ValueError("development packet rejected: " + "; ".join(errors))

        hash_payload = {
            "packet_id": packet_id,
            "business_process": asdict(business_process),
            "algorithm": asdict(algorithm),
            "architecture": asdict(architecture),
            "test_contract": asdict(test_contract),
            "system_analysis_approved": system_analysis_approved,
        }
        digest = sha256(_canonical(hash_payload).encode("utf-8")).hexdigest()

        return DevelopmentPacket(
            packet_id=packet_id,
            business_process=business_process,
            algorithm=algorithm,
            architecture=architecture,
            test_contract=test_contract,
            system_analysis_approved=system_analysis_approved,
            packet_hash=digest,
        )
