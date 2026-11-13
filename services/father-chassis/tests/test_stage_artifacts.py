import pytest

from father.engineering.delivery_contract import (
    AcceptanceCriterion,
    AlgorithmSpec,
    ArchitectureSpec,
    BusinessProcessSpec,
    DevelopmentPacketBuilder,
    InterfaceContract,
    TestContract as EngineeringTestContract,
    VariableContract,
)
from father.engineering.stage_artifacts import (
    CustomerRequestPayload,
    SystemAnalysisPackage,
    deserialize_stage_payload,
    serialize_stage_payload,
)


def test_customer_request_round_trip_is_typed():
    payload = CustomerRequestPayload(
        request_id="REQ-TA-1",
        title="Typed artifact",
        objective="Eliminate dict handoff",
    )
    raw = serialize_stage_payload("customer_request", 1, payload)
    restored = deserialize_stage_payload("customer_request", 1, raw)
    assert restored == payload
    assert isinstance(restored, CustomerRequestPayload)


def test_wrong_payload_type_is_rejected():
    with pytest.raises(TypeError, match="requires CustomerRequestPayload"):
        serialize_stage_payload("customer_request", 1, {"request_id": "bad"})


def test_unknown_schema_version_is_rejected():
    payload = CustomerRequestPayload("REQ-1", "title", "objective")
    with pytest.raises(ValueError, match="unsupported artifact schema"):
        serialize_stage_payload("customer_request", 99, payload)


def test_system_analysis_round_trip_is_typed():
    payload = SystemAnalysisPackage(
        analysis_id="SYS-1",
        functional_requirements=("FR-1",),
        nonfunctional_requirements=("NFR-1",),
        states=("READY",),
        events=("START",),
        data_entities=("Artifact",),
        interfaces=("IF-1",),
        failure_modes=("invalid_schema",),
        approved=True,
    )
    restored = deserialize_stage_payload(
        "SystemAnalysisPackage",
        1,
        serialize_stage_payload("SystemAnalysisPackage", 1, payload),
    )
    assert restored == payload
    assert isinstance(restored, SystemAnalysisPackage)


def test_architecture_nested_types_survive_round_trip():
    variable = VariableContract(
        name="recipe_hash",
        type_name="str",
        owner_block="ProductRegistry",
        direction="input",
    )
    interface = InterfaceContract(
        interface_id="IF-1",
        producer="Composer",
        consumer="ProductRegistry",
        request_schema=(variable,),
        response_schema=(),
    )
    payload = ArchitectureSpec(
        architecture_id="ARCH-1",
        algorithm_id="ALG-1",
        blocks=("Composer", "ProductRegistry"),
        interfaces=(interface,),
        states=("READY",),
        approved=True,
    )
    restored = deserialize_stage_payload(
        "ArchitectureSpec",
        1,
        serialize_stage_payload("ArchitectureSpec", 1, payload),
    )
    assert isinstance(restored, ArchitectureSpec)
    assert isinstance(restored.interfaces[0], InterfaceContract)
    assert isinstance(restored.interfaces[0].request_schema[0], VariableContract)


def test_development_packet_nested_types_survive_round_trip():
    process = BusinessProcessSpec(
        process_id="BP-1",
        goal="typed handoff",
        inputs=("in",),
        outputs=("out",),
        actors=("factory",),
        approved=True,
    )
    algorithm = AlgorithmSpec(
        algorithm_id="ALG-1",
        process_id="BP-1",
        preconditions=("ready",),
        steps=("execute",),
        postconditions=("done",),
        approved=True,
    )
    interface = InterfaceContract(
        interface_id="IF-1",
        producer="A",
        consumer="B",
        request_schema=(
            VariableContract("x", "str", "A", "input"),
        ),
        response_schema=(),
    )
    architecture = ArchitectureSpec(
        architecture_id="ARCH-1",
        algorithm_id="ALG-1",
        blocks=("A", "B"),
        interfaces=(interface,),
        states=("READY",),
        approved=True,
    )
    tests = EngineeringTestContract(
        test_contract_id="TEST-1",
        architecture_id="ARCH-1",
        criteria=(
            AcceptanceCriterion("AC-1", "works", "success", "==", 1, "unit"),
        ),
        approved=True,
    )
    packet = DevelopmentPacketBuilder.build(
        packet_id="DEV-1",
        business_process=process,
        algorithm=algorithm,
        architecture=architecture,
        test_contract=tests,
        system_analysis_approved=True,
    )
    restored = deserialize_stage_payload(
        "DevelopmentPacket",
        1,
        serialize_stage_payload("DevelopmentPacket", 1, packet),
    )
    assert restored == packet
    assert isinstance(restored.architecture, ArchitectureSpec)
    assert isinstance(restored.test_contract, EngineeringTestContract)
