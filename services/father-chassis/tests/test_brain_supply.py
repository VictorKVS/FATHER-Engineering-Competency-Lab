from dataclasses import replace

from father.brain_factory.supply import (
    AgentBrainRequest,
    BrainPackageDescriptor,
    BrainSupplyPolicy,
    DeterministicBrainSupplyResolver,
)


def _request(**changes):
    base = AgentBrainRequest(
        request_id="REQ-1",
        agent_id="AGENT-1",
        agent_class="A3",
        requested_brain_class="B3",
        role="ANALYST",
        domains=("SECURITY",),
        required_capabilities=("VECTOR", "GRAPH"),
        supply_mode="TASK_SCOPED",
        tenant_id="TENANT-A",
        authorized_classifications=("PUBLIC", "INTERNAL"),
    )
    return replace(base, **changes)


def _package(**changes):
    base = BrainPackageDescriptor(
        package_id="FBP-SEC-001",
        version="1.0.0",
        brain_class="B3",
        domains=("SECURITY", "OSINT"),
        capabilities=("VECTOR", "GRAPH", "LEXICAL"),
        supported_supply_modes=("BASELINE", "TASK_SCOPED"),
        compatible_agent_classes=("A3",),
        allowed_roles=("ANALYST",),
        classification="INTERNAL",
        tenant_scope="TENANT-A",
        lifecycle_state="QUALIFIED",
    )
    return replace(base, **changes)


def _resolve(request=None, packages=None, policy=None):
    return DeterministicBrainSupplyResolver().resolve(
        request or _request(),
        packages or (_package(),),
        policy or BrainSupplyPolicy("POL-SUPPLY", "1.0"),
    )


def test_exact_eligible_package_binds():
    result = _resolve()
    assert result.status == "BOUND"
    assert result.selected_package_id == "FBP-SEC-001"


def test_agent_class_and_brain_class_are_independent():
    result = _resolve()
    assert _request().agent_class == "A3"
    assert _request().requested_brain_class == "B3"
    assert result.status == "BOUND"


def test_wrong_brain_class_is_blocked():
    result = _resolve(packages=(_package(brain_class="B4"),))
    assert result.status == "NO_MATCH"


def test_wrong_agent_class_compatibility_is_blocked():
    result = _resolve(packages=(_package(compatible_agent_classes=("A4",)),))
    assert result.status == "NO_MATCH"


def test_no_silent_higher_brain_class_fallback():
    result = _resolve(
        packages=(_package(brain_class="B4", compatible_agent_classes=("A3",)),)
    )
    assert result.status == "NO_MATCH"


def test_missing_capability_is_blocked():
    assert _resolve(packages=(_package(capabilities=("VECTOR",)),)).status == "NO_MATCH"


def test_wrong_domain_is_blocked():
    assert _resolve(packages=(_package(domains=("LEGAL",)),)).status == "NO_MATCH"


def test_wrong_role_is_blocked():
    assert _resolve(packages=(_package(allowed_roles=("ADMIN",)),)).status == "NO_MATCH"


def test_unsupported_supply_mode_is_blocked():
    result = _resolve(packages=(_package(supported_supply_modes=("BASELINE",)),))
    assert result.status == "NO_MATCH"


def test_unauthorized_classification_is_blocked():
    result = _resolve(packages=(_package(classification="CONFIDENTIAL"),))
    assert result.status == "NO_MATCH"


def test_cross_tenant_binding_is_blocked():
    assert _resolve(packages=(_package(tenant_scope="TENANT-B"),)).status == "NO_MATCH"


def test_global_tenant_package_can_be_allowed():
    assert _resolve(packages=(_package(tenant_scope="*"),)).status == "BOUND"


def test_global_tenant_package_can_be_disabled():
    policy = BrainSupplyPolicy(
        "POL-SUPPLY",
        "1.0",
        allow_global_tenant_packages=False,
    )
    result = _resolve(packages=(_package(tenant_scope="*"),), policy=policy)
    assert result.status == "NO_MATCH"


def test_revoked_package_is_blocked():
    assert _resolve(packages=(_package(lifecycle_state="REVOKED"),)).status == "NO_MATCH"


def test_draft_package_is_blocked():
    assert _resolve(packages=(_package(lifecycle_state="DRAFT"),)).status == "NO_MATCH"


def test_input_order_does_not_change_bound_decision_identity():
    exact = _package(package_id="FBP-EXACT", capabilities=("VECTOR", "GRAPH"))
    broader = _package(
        package_id="FBP-BROAD",
        capabilities=("VECTOR", "GRAPH", "LEXICAL"),
    )
    first = _resolve(packages=(broader, exact))
    second = _resolve(packages=(exact, broader))
    assert first.status == second.status == "BOUND"
    assert first.selected_package_id == second.selected_package_id == "FBP-EXACT"
    assert first.decision_hash == second.decision_hash
    assert first.decision_id == second.decision_id


def test_policy_version_changes_decision_identity():
    first = _resolve(policy=BrainSupplyPolicy("POL-SUPPLY", "1.0"))
    second = _resolve(policy=BrainSupplyPolicy("POL-SUPPLY", "2.0"))
    assert first.status == second.status == "BOUND"
    assert first.decision_hash != second.decision_hash


def test_requested_brain_class_changes_decision_identity():
    first = _resolve()
    second = _resolve(request=_request(requested_brain_class="B2"))
    assert second.status == "NO_MATCH"
    assert first.decision_hash != second.decision_hash


def test_equal_best_candidates_are_ambiguous():
    a = _package(package_id="FBP-A", capabilities=("VECTOR", "GRAPH"))
    b = _package(package_id="FBP-B", capabilities=("VECTOR", "GRAPH"))
    result = _resolve(packages=(a, b))
    assert result.status == "AMBIGUOUS"
    assert result.selected_package_id is None


def test_invalid_request_is_rejected():
    assert _resolve(request=_request(agent_id="")).status == "REJECTED"


def test_invalid_policy_is_rejected():
    policy = BrainSupplyPolicy("POL-SUPPLY", "1.0", require_exact_brain_class=False)
    assert _resolve(policy=policy).status == "REJECTED"
