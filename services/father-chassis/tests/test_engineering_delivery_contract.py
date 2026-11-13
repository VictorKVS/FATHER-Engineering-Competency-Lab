import pytest

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


def _valid_packet():
    process = BusinessProcessSpec(
        process_id="BP-PRODUCT-REGISTER",
        goal="Persist product identity across runtime restart",
        inputs=("product_recipe",),
        outputs=("product_registration",),
        actors=("factory", "product_registry"),
        success_metrics={"restore_success": 1.0},
        approved=True,
    )
    algorithm = AlgorithmSpec(
        algorithm_id="ALG-PRODUCT-REGISTER",
        process_id=process.process_id,
        preconditions=("recipe_hash exists",),
        steps=(
            "derive product/version key",
            "load existing registration",
            "reject hash conflict",
            "persist when absent",
            "return registration",
        ),
        postconditions=("same product/version maps to same recipe hash",),
        invariants=("conflicting recipe hash is rejected",),
        approved=True,
    )
    request = VariableContract(
        name="recipe_hash",
        type_name="str",
        owner_block="ProductRegistry",
        direction="input",
    )
    response = VariableContract(
        name="registration",
        type_name="ProductRegistration",
        owner_block="ProductRegistry",
        direction="output",
    )
    interface = InterfaceContract(
        interface_id="IF-REGISTRY-REGISTER",
        producer="ProductComposer",
        consumer="ProductRegistry",
        request_schema=(request,),
        response_schema=(response,),
        errors=("ProductVersionConflict",),
        latency_slo_ms=50,
    )
    architecture = ArchitectureSpec(
        architecture_id="ARCH-PRODUCT-REGISTER",
        algorithm_id=algorithm.algorithm_id,
        blocks=("ProductComposer", "ProductRegistry"),
        interfaces=(interface,),
        states=("ABSENT", "ASSEMBLED", "CONFLICT"),
        constants={"namespace": "product_registry"},
        approved=True,
    )
    tests = TestContract(
        test_contract_id="TEST-PRODUCT-REGISTER",
        architecture_id=architecture.architecture_id,
        criteria=(
            AcceptanceCriterion(
                criterion_id="AC-RESTORE",
                statement="Registration survives runtime reopen",
                metric="restore_success",
                operator="==",
                threshold=1,
                evidence_type="integration_test",
            ),
            AcceptanceCriterion(
                criterion_id="AC-CONFLICT",
                statement="Conflicting recipe hash is rejected",
                metric="conflict_rejection",
                operator="==",
                threshold=1,
                evidence_type="negative_test",
            ),
        ),
        approved=True,
    )
    return process, algorithm, architecture, tests


def test_approved_packet_is_hash_bound_and_buildable():
    process, algorithm, architecture, tests = _valid_packet()
    packet = DevelopmentPacketBuilder.build(
        packet_id="DEV-PACKET-001",
        business_process=process,
        algorithm=algorithm,
        architecture=architecture,
        test_contract=tests,
        system_analysis_approved=True,
    )
    assert packet.packet_hash
    assert packet.architecture.interfaces[0].request_schema[0].name == "recipe_hash"


def test_programmer_cannot_receive_unapproved_or_incomplete_packet():
    process, algorithm, architecture, tests = _valid_packet()
    broken = ArchitectureSpec(
        architecture_id=architecture.architecture_id,
        algorithm_id=architecture.algorithm_id,
        blocks=architecture.blocks,
        interfaces=(),
        states=architecture.states,
        approved=True,
    )
    with pytest.raises(ValueError, match="architecture interfaces are required"):
        DevelopmentPacketBuilder.build(
            packet_id="DEV-PACKET-BROKEN",
            business_process=process,
            algorithm=algorithm,
            architecture=broken,
            test_contract=tests,
            system_analysis_approved=True,
        )


def test_unknown_variable_owner_is_rejected_before_coding():
    process, algorithm, architecture, tests = _valid_packet()
    bad_variable = VariableContract(
        name="recipe_hash",
        type_name="str",
        owner_block="ImaginaryBlock",
        direction="input",
    )
    bad_interface = InterfaceContract(
        interface_id="IF-BAD",
        producer="ProductComposer",
        consumer="ProductRegistry",
        request_schema=(bad_variable,),
        response_schema=(),
    )
    broken = ArchitectureSpec(
        architecture_id=architecture.architecture_id,
        algorithm_id=architecture.algorithm_id,
        blocks=architecture.blocks,
        interfaces=(bad_interface,),
        states=architecture.states,
        approved=True,
    )
    with pytest.raises(ValueError, match="owner block is unknown"):
        DevelopmentPacketBuilder.build(
            packet_id="DEV-PACKET-BAD-VAR",
            business_process=process,
            algorithm=algorithm,
            architecture=broken,
            test_contract=tests,
            system_analysis_approved=True,
        )
