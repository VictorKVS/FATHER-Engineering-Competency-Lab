from dataclasses import replace

from father.brain_factory.storage_selection import (
    DeterministicStorageProfileSelector,
    StorageProfileDescriptor,
    StorageSelectionPolicy,
    StorageSelectionRequest,
)


def _request(**changes):
    base = StorageSelectionRequest(
        "STREQ-1", "B1", "EDGE", ("RELATIONAL", "OBJECT"),
        10000, 1, 100, 2048, 32, True, False, False, True
    )
    return replace(base, **changes)


def _profile(**changes):
    base = StorageProfileDescriptor(
        "SP-EDGE-LITE", ("B1",), ("EDGE",), ("RELATIONAL", "OBJECT"),
        512, 2, 100000, 5, True, False, False, "LOW", 1,
        "QUALIFIED", "QUALIFIED"
    )
    return replace(base, **changes)


def _select(request=None, profiles=None, policy=None):
    return DeterministicStorageProfileSelector().select(
        request or _request(),
        profiles or (_profile(),),
        policy or StorageSelectionPolicy("POL-STORAGE", "1.0"),
    )


def test_edge_profile_selected_and_explained():
    result = _select()
    assert result.status == "SELECTED"
    assert result.selected_profile_id == "SP-EDGE-LITE"
    assert result.selection_reasons


def test_ram_and_storage_limits_enforced():
    assert _select(profiles=(_profile(min_ram_mb=4096),)).status == "NO_MATCH"
    assert _select(profiles=(_profile(min_storage_gb=64),)).status == "NO_MATCH"


def test_corpus_and_concurrency_envelopes_enforced():
    assert _select(request=_request(corpus_chunks=200000)).status == "NO_MATCH"
    assert _select(request=_request(concurrent_users=10)).status == "NO_MATCH"


def test_offline_ha_assurance_power_constraints_enforced():
    assert _select(profiles=(_profile(supports_offline=False),)).status == "NO_MATCH"
    assert _select(
        request=_request(high_availability_required=True),
        profiles=(_profile(supports_ha=False),),
    ).status == "NO_MATCH"
    assert _select(
        request=_request(high_assurance_required=True),
        profiles=(_profile(supports_high_assurance=False),),
    ).status == "NO_MATCH"
    assert _select(profiles=(_profile(power_class="MEDIUM"),)).status == "NO_MATCH"


def test_capability_and_evidence_constraints_enforced():
    assert _select(request=_request(required_capabilities=("GRAPH",))).status == "NO_MATCH"
    assert _select(profiles=(_profile(evidence_state="MEASURED"),)).status == "NO_MATCH"


def test_brain_and_deployment_profile_match_enforced():
    assert _select(
        profiles=(_profile(supported_brain_classes=("B2",)),)
    ).status == "NO_MATCH"
    assert _select(
        profiles=(_profile(deployment_profiles=("STANDARD",)),)
    ).status == "NO_MATCH"


def test_minimal_sufficient_profile_is_preferred():
    small = _profile(profile_id="SP-SMALL", operational_complexity=1, min_ram_mb=512)
    large = _profile(profile_id="SP-LARGE", operational_complexity=3, min_ram_mb=1024)
    result = _select(profiles=(large, small))
    assert result.status == "SELECTED"
    assert result.selected_profile_id == "SP-SMALL"


def test_equal_best_profiles_are_ambiguous():
    result = _select(profiles=(_profile(profile_id="SP-A"), _profile(profile_id="SP-B")))
    assert result.status == "AMBIGUOUS"


def test_rejected_alternatives_are_explained():
    bad = _profile(profile_id="SP-BAD", min_ram_mb=4096)
    good = _profile(profile_id="SP-GOOD")
    result = _select(profiles=(bad, good))
    rejected = {x.profile_id: x.reasons for x in result.rejected_alternatives}
    assert "ram_ceiling_exceeded" in rejected["SP-BAD"]


def test_input_order_is_irrelevant():
    small = _profile(profile_id="SP-SMALL", operational_complexity=1)
    large = _profile(profile_id="SP-LARGE", operational_complexity=2)
    a = _select(profiles=(large, small))
    b = _select(profiles=(small, large))
    assert a.decision_hash == b.decision_hash
    assert a.selected_profile_id == b.selected_profile_id == "SP-SMALL"


def test_policy_version_changes_identity():
    a = _select(policy=StorageSelectionPolicy("POL-STORAGE", "1.0"))
    b = _select(policy=StorageSelectionPolicy("POL-STORAGE", "2.0"))
    assert a.decision_hash != b.decision_hash


def test_invalid_request_rejected():
    assert _select(request=_request(concurrent_users=0)).status == "REJECTED"
