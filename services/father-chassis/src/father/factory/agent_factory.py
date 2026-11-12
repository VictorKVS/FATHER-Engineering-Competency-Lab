from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from father.core.agent_manifest import AgentManifest
from father.core.capabilities import CapabilityRegistry
from father.core.providers import ProviderRegistry


@dataclass(frozen=True, slots=True)
class ProviderBinding:
    capability: str
    provider_id: str
    provider_kind: str
    provider_version: str


@dataclass(frozen=True, slots=True)
class AgentBuildPlan:
    agent_id: str
    agent_version: str
    capabilities: tuple[str, ...]
    permissions: tuple[str, ...]
    provider_bindings: tuple[ProviderBinding, ...]
    approval_required_for: tuple[str, ...]
    max_steps: int
    timeout_seconds: int
    max_cost_usd: float | None
    buildable: bool
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_version": self.agent_version,
            "capabilities": list(self.capabilities),
            "permissions": list(self.permissions),
            "provider_bindings": [asdict(x) for x in self.provider_bindings],
            "approval_required_for": list(self.approval_required_for),
            "max_steps": self.max_steps,
            "timeout_seconds": self.timeout_seconds,
            "max_cost_usd": self.max_cost_usd,
            "buildable": self.buildable,
            "errors": list(self.errors),
        }


@dataclass(frozen=True, slots=True)
class ExecutableAgentProfile:
    manifest: AgentManifest
    build_plan: AgentBuildPlan

    @property
    def agent_id(self) -> str:
        return self.manifest.agent_id


class AgentFactory:
    """Builds an executable agent profile from contracts, not from vendor-specific code."""

    def __init__(
        self,
        capabilities: CapabilityRegistry,
        providers: ProviderRegistry,
    ) -> None:
        self.capabilities = capabilities
        self.providers = providers

    def plan(self, manifest: AgentManifest) -> AgentBuildPlan:
        errors = list(manifest.validate(self.capabilities))
        bindings: list[ProviderBinding] = []

        for capability_name in sorted(manifest.capabilities):
            capability = next(
                (c for c in self.capabilities.list() if c.name == capability_name),
                None,
            )
            if capability is None:
                continue

            if capability.provider_kind == "internal":
                continue

            try:
                provider = self.providers.resolve(
                    kind=capability.provider_kind,
                    capability=capability.name,
                )
            except LookupError as exc:
                errors.append(str(exc))
                continue

            bindings.append(
                ProviderBinding(
                    capability=capability.name,
                    provider_id=provider.descriptor.provider_id,
                    provider_kind=provider.descriptor.provider_kind,
                    provider_version=provider.descriptor.version,
                )
            )

        for required_provider in sorted(manifest.required_providers):
            if required_provider not in {x.provider_id for x in bindings}:
                errors.append(f"required provider not bound: {required_provider}")

        return AgentBuildPlan(
            agent_id=manifest.agent_id,
            agent_version=manifest.version,
            capabilities=tuple(sorted(manifest.capabilities)),
            permissions=tuple(sorted(manifest.required_permissions)),
            provider_bindings=tuple(bindings),
            approval_required_for=tuple(sorted(manifest.approval_required_for)),
            max_steps=manifest.max_steps,
            timeout_seconds=manifest.timeout_seconds,
            max_cost_usd=manifest.max_cost_usd,
            buildable=not errors,
            errors=tuple(errors),
        )

    def build(self, manifest: AgentManifest) -> ExecutableAgentProfile:
        plan = self.plan(manifest)
        if not plan.buildable:
            raise ValueError("agent build failed: " + "; ".join(plan.errors))
        return ExecutableAgentProfile(manifest=manifest, build_plan=plan)
