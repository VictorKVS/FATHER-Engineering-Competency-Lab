from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ClearanceLevel(IntEnum):
    PUBLIC = 0
    INTERNAL = 10
    RESTRICTED = 20
    CONFIDENTIAL = 30
    SECRET = 40
    CRITICAL = 50


@dataclass(frozen=True, slots=True)
class SubjectContext:
    subject_id: str
    roles: frozenset[str]
    clearance: ClearanceLevel
    organizations: frozenset[str] = frozenset()
    projects: frozenset[str] = frozenset()
    compartments: frozenset[str] = frozenset()
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ResourceContext:
    resource_id: str
    classification: ClearanceLevel
    owner_org: str | None = None
    project_id: str | None = None
    compartments: frozenset[str] = frozenset()
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AccessDecision:
    allowed: bool
    reason: str
    matched_role: str | None = None


DEFAULT_ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "viewer": frozenset({
        "read:public",
        "read:report",
    }),
    "analyst": frozenset({
        "read:public",
        "read:report",
        "read:evidence",
        "execute:analysis",
        "execute:search",
    }),
    "security_specialist": frozenset({
        "read:public",
        "read:report",
        "read:evidence",
        "read:compliance",
        "execute:analysis",
        "execute:search",
        "execute:control_assessment",
        "propose:decision",
    }),
    "security_architect": frozenset({
        "*",
        "approve:decision",
        "manage:policy",
    }),
    "auditor": frozenset({
        "read:report",
        "read:evidence",
        "read:audit",
        "read:compliance",
        "verify:decision_trace",
    }),
    "operator": frozenset({
        "execute:workflow",
        "execute:tool",
        "read:operational",
    }),
    "admin": frozenset({"*"}),
}


class AccessControl:
    def __init__(self, role_permissions: dict[str, frozenset[str]] | None = None) -> None:
        self.role_permissions = dict(role_permissions or DEFAULT_ROLE_PERMISSIONS)

    def _role_allows(self, roles: frozenset[str], permission: str) -> str | None:
        for role in roles:
            perms = self.role_permissions.get(role, frozenset())
            if "*" in perms or permission in perms:
                return role
        return None

    def authorize(
        self,
        *,
        subject: SubjectContext,
        resource: ResourceContext,
        permission: str,
    ) -> AccessDecision:
        role = self._role_allows(subject.roles, permission)
        if role is None:
            return AccessDecision(False, f"permission denied: {permission}")

        if subject.clearance < resource.classification:
            return AccessDecision(
                False,
                f"clearance {subject.clearance.name} below resource classification {resource.classification.name}",
                role,
            )

        if role == "admin":
            return AccessDecision(True, "allowed", role)

        if resource.owner_org and resource.owner_org not in subject.organizations:
            return AccessDecision(False, "organization scope mismatch", role)

        if resource.project_id and resource.project_id not in subject.projects:
            return AccessDecision(False, "project scope mismatch", role)

        if resource.compartments and not resource.compartments.issubset(subject.compartments):
            return AccessDecision(False, "missing required compartment access", role)

        return AccessDecision(True, "allowed", role)

    def require(self, *, subject: SubjectContext, resource: ResourceContext, permission: str) -> None:
        decision = self.authorize(subject=subject, resource=resource, permission=permission)
        if not decision.allowed:
            raise PermissionError(decision.reason)
