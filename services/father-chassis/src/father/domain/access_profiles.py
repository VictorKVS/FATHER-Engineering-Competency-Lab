from __future__ import annotations

from father.core.access_control import ClearanceLevel, SubjectContext


def viewer(subject_id: str) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"viewer"}),
        clearance=ClearanceLevel.PUBLIC,
    )


def analyst(subject_id: str, *, projects: set[str] | None = None) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"analyst"}),
        clearance=ClearanceLevel.INTERNAL,
        projects=frozenset(projects or set()),
    )


def security_specialist(subject_id: str, *, projects: set[str] | None = None) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"security_specialist"}),
        clearance=ClearanceLevel.RESTRICTED,
        projects=frozenset(projects or set()),
    )


def security_architect(subject_id: str, *, compartments: set[str] | None = None) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"security_architect"}),
        clearance=ClearanceLevel.CONFIDENTIAL,
        compartments=frozenset(compartments or set()),
    )


def auditor(subject_id: str) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"auditor"}),
        clearance=ClearanceLevel.RESTRICTED,
    )


def admin(subject_id: str) -> SubjectContext:
    return SubjectContext(
        subject_id=subject_id,
        roles=frozenset({"admin"}),
        clearance=ClearanceLevel.CRITICAL,
    )
