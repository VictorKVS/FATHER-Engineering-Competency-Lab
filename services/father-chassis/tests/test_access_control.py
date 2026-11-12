import pytest

from father.core.access_control import (
    AccessControl,
    ClearanceLevel,
    ResourceContext,
    SubjectContext,
)


def test_role_and_clearance_both_required():
    acl = AccessControl()

    subject = SubjectContext(
        subject_id="u1",
        roles=frozenset({"analyst"}),
        clearance=ClearanceLevel.INTERNAL,
        projects=frozenset({"p1"}),
    )
    resource = ResourceContext(
        resource_id="r1",
        classification=ClearanceLevel.RESTRICTED,
        project_id="p1",
    )

    decision = acl.authorize(subject=subject, resource=resource, permission="read:evidence")
    assert decision.allowed is False
    assert "clearance" in decision.reason


def test_project_scope_is_enforced():
    acl = AccessControl()

    subject = SubjectContext(
        subject_id="u2",
        roles=frozenset({"security_specialist"}),
        clearance=ClearanceLevel.RESTRICTED,
        projects=frozenset({"p1"}),
    )
    resource = ResourceContext(
        resource_id="r2",
        classification=ClearanceLevel.RESTRICTED,
        project_id="p2",
    )

    decision = acl.authorize(subject=subject, resource=resource, permission="read:evidence")
    assert decision.allowed is False
    assert decision.reason == "project scope mismatch"


def test_compartment_access_is_enforced():
    acl = AccessControl()

    subject = SubjectContext(
        subject_id="u3",
        roles=frozenset({"security_architect"}),
        clearance=ClearanceLevel.CONFIDENTIAL,
        compartments=frozenset({"KII"}),
    )
    resource = ResourceContext(
        resource_id="r3",
        classification=ClearanceLevel.CONFIDENTIAL,
        compartments=frozenset({"KII", "INCIDENT"}),
    )

    decision = acl.authorize(subject=subject, resource=resource, permission="approve:decision")
    assert decision.allowed is False
    assert "compartment" in decision.reason


def test_admin_can_access_critical_resource():
    acl = AccessControl()

    subject = SubjectContext(
        subject_id="admin",
        roles=frozenset({"admin"}),
        clearance=ClearanceLevel.CRITICAL,
    )
    resource = ResourceContext(
        resource_id="critical",
        classification=ClearanceLevel.CRITICAL,
    )

    acl.require(subject=subject, resource=resource, permission="manage:policy")
