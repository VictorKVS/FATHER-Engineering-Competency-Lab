from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _stable_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({value.strip() for value in values if value.strip()}))


@dataclass(frozen=True, slots=True)
class AgentBrainRequest:
    request_id: str
    agent_id: str
    agent_class: str
    requested_brain_class: str
    role: str
    domains: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    supply_mode: str
    tenant_id: str
    authorized_classifications: tuple[str, ...]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name, value in (
            ("request_id", self.request_id),
            ("agent_id", self.agent_id),
            ("agent_class", self.agent_class),
            ("requested_brain_class", self.requested_brain_class),
            ("role", self.role),
            ("supply_mode", self.supply_mode),
            ("tenant_id", self.tenant_id),
        ):
            if not value.strip():
                errors.append(f"{field_name} is required")
        if not _stable_tuple(self.domains):
            errors.append("at least one domain is required")
        if not _stable_tuple(self.authorized_classifications):
            errors.append("at least one authorized classification is required")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class BrainPackageDescriptor:
    package_id: str
    version: str
    brain_class: str
    domains: tuple[str, ...]
    capabilities: tuple[str, ...]
    supported_supply_modes: tuple[str, ...]
    compatible_agent_classes: tuple[str, ...]
    allowed_roles: tuple[str, ...]
    classification: str
    tenant_scope: str
    lifecycle_state: str

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name, value in (
            ("package_id", self.package_id),
            ("version", self.version),
            ("brain_class", self.brain_class),
            ("classification", self.classification),
            ("tenant_scope", self.tenant_scope),
            ("lifecycle_state", self.lifecycle_state),
        ):
            if not value.strip():
                errors.append(f"{field_name} is required")
        if not _stable_tuple(self.domains):
            errors.append("package domains are required")
        if not _stable_tuple(self.supported_supply_modes):
            errors.append("supported_supply_modes are required")
        if not _stable_tuple(self.compatible_agent_classes):
            errors.append("compatible_agent_classes are required")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class BrainSupplyPolicy:
    policy_id: str
    version: str
    eligible_states: tuple[str, ...] = ("QUALIFIED", "RELEASED")
    require_exact_brain_class: bool = True
    allow_global_tenant_packages: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("policy version is required")
        if not _stable_tuple(self.eligible_states):
            errors.append("eligible_states are required")
        if not self.require_exact_brain_class:
            errors.append("reference v1 requires exact brain class")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class BrainSupplyDecision:
    status: str
    selected_package_id: str | None
    selected_version: str | None
    decision_id: str
    decision_hash: str
    diagnostics: tuple[str, ...] = ()


class DeterministicBrainSupplyResolver:
    @staticmethod
    def _decision(
        *,
        status: str,
        request: AgentBrainRequest,
        policy: BrainSupplyPolicy,
        selected: BrainPackageDescriptor | None,
        eligible: tuple[BrainPackageDescriptor, ...],
        diagnostics: tuple[str, ...] = (),
    ) -> BrainSupplyDecision:
        payload = {
            "status": status,
            "request": {
                "request_id": request.request_id,
                "agent_id": request.agent_id,
                "agent_class": request.agent_class,
                "requested_brain_class": request.requested_brain_class,
                "role": request.role,
                "domains": _stable_tuple(request.domains),
                "required_capabilities": _stable_tuple(request.required_capabilities),
                "supply_mode": request.supply_mode,
                "tenant_id": request.tenant_id,
                "authorized_classifications": _stable_tuple(
                    request.authorized_classifications
                ),
            },
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "selected": (
                None
                if selected is None
                else {
                    "package_id": selected.package_id,
                    "version": selected.version,
                }
            ),
            "eligible": tuple(
                sorted((item.package_id, item.version) for item in eligible)
            ),
            "diagnostics": tuple(sorted(diagnostics)),
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return BrainSupplyDecision(
            status=status,
            selected_package_id=None if selected is None else selected.package_id,
            selected_version=None if selected is None else selected.version,
            decision_id=f"SUPPLY-{digest[:16]}",
            decision_hash=digest,
            diagnostics=tuple(sorted(diagnostics)),
        )

    @staticmethod
    def _package_eligible(
        request: AgentBrainRequest,
        package: BrainPackageDescriptor,
        policy: BrainSupplyPolicy,
    ) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []
        if package.lifecycle_state not in _stable_tuple(policy.eligible_states):
            reasons.append("lifecycle_state")
        if (
            policy.require_exact_brain_class
            and package.brain_class != request.requested_brain_class
        ):
            reasons.append("brain_class")
        if request.agent_class not in _stable_tuple(package.compatible_agent_classes):
            reasons.append("agent_class")
        if package.allowed_roles and request.role not in _stable_tuple(package.allowed_roles):
            reasons.append("role")
        if request.supply_mode not in _stable_tuple(package.supported_supply_modes):
            reasons.append("supply_mode")

        package_domains = set(_stable_tuple(package.domains))
        if not set(_stable_tuple(request.domains)).issubset(package_domains):
            reasons.append("domain")

        package_capabilities = set(_stable_tuple(package.capabilities))
        if not set(_stable_tuple(request.required_capabilities)).issubset(
            package_capabilities
        ):
            reasons.append("capability")

        if package.classification not in _stable_tuple(
            request.authorized_classifications
        ):
            reasons.append("classification")

        tenant_ok = package.tenant_scope == request.tenant_id
        if package.tenant_scope == "*" and policy.allow_global_tenant_packages:
            tenant_ok = True
        if not tenant_ok:
            reasons.append("tenant")

        return not reasons, tuple(sorted(reasons))

    def resolve(
        self,
        request: AgentBrainRequest,
        candidates: tuple[BrainPackageDescriptor, ...],
        policy: BrainSupplyPolicy,
    ) -> BrainSupplyDecision:
        validation = list(request.validate()) + list(policy.validate())
        for package in candidates:
            validation.extend(
                f"{package.package_id}: {error}" for error in package.validate()
            )
        if validation:
            return self._decision(
                status="REJECTED",
                request=request,
                policy=policy,
                selected=None,
                eligible=(),
                diagnostics=tuple(validation),
            )

        eligible: list[BrainPackageDescriptor] = []
        rejected_reasons: list[str] = []
        for package in sorted(candidates, key=lambda item: (item.package_id, item.version)):
            accepted, reasons = self._package_eligible(request, package, policy)
            if accepted:
                eligible.append(package)
            else:
                rejected_reasons.append(
                    f"{package.package_id}@{package.version}:" + ",".join(reasons)
                )

        if not eligible:
            return self._decision(
                status="NO_MATCH",
                request=request,
                policy=policy,
                selected=None,
                eligible=(),
                diagnostics=tuple(rejected_reasons),
            )

        required_caps = set(_stable_tuple(request.required_capabilities))

        def rank(package: BrainPackageDescriptor) -> tuple[int, int]:
            exact_tenant_penalty = 0 if package.tenant_scope == request.tenant_id else 1
            excess_capabilities = len(
                set(_stable_tuple(package.capabilities)) - required_caps
            )
            return exact_tenant_penalty, excess_capabilities

        ranked = sorted(
            eligible,
            key=lambda package: (rank(package), package.package_id, package.version),
        )
        best_rank = rank(ranked[0])
        best = tuple(package for package in ranked if rank(package) == best_rank)

        if len(best) != 1:
            return self._decision(
                status="AMBIGUOUS",
                request=request,
                policy=policy,
                selected=None,
                eligible=tuple(eligible),
                diagnostics=tuple(
                    f"equally eligible: {item.package_id}@{item.version}"
                    for item in best
                ),
            )

        return self._decision(
            status="BOUND",
            request=request,
            policy=policy,
            selected=best[0],
            eligible=tuple(eligible),
        )
