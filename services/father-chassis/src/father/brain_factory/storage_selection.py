from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _stable_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({value.strip() for value in values if value.strip()}))


@dataclass(frozen=True, slots=True)
class StorageSelectionRequest:
    request_id: str
    brain_class: str
    deployment_profile: str
    required_capabilities: tuple[str, ...]
    corpus_chunks: int
    concurrent_users: int
    target_p95_ms: int
    max_ram_mb: int | None = None
    max_storage_gb: int | None = None
    offline_required: bool = False
    high_availability_required: bool = False
    high_assurance_required: bool = False
    power_constrained: bool = False

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for name, value in (
            ("request_id", self.request_id),
            ("brain_class", self.brain_class),
            ("deployment_profile", self.deployment_profile),
        ):
            if not value.strip():
                errors.append(f"{name} is required")
        if self.corpus_chunks < 0:
            errors.append("corpus_chunks must be >= 0")
        if self.concurrent_users < 1:
            errors.append("concurrent_users must be >= 1")
        if self.target_p95_ms < 1:
            errors.append("target_p95_ms must be >= 1")
        if self.max_ram_mb is not None and self.max_ram_mb < 1:
            errors.append("max_ram_mb must be >= 1")
        if self.max_storage_gb is not None and self.max_storage_gb < 1:
            errors.append("max_storage_gb must be >= 1")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class StorageProfileDescriptor:
    profile_id: str
    supported_brain_classes: tuple[str, ...]
    deployment_profiles: tuple[str, ...]
    capabilities: tuple[str, ...]
    min_ram_mb: int
    min_storage_gb: int
    max_corpus_chunks: int
    max_concurrent_users: int
    supports_offline: bool
    supports_ha: bool
    supports_high_assurance: bool
    power_class: str
    operational_complexity: int
    lifecycle_state: str
    evidence_state: str

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.profile_id.strip():
            errors.append("profile_id is required")
        if not _stable_tuple(self.supported_brain_classes):
            errors.append("supported_brain_classes are required")
        if not _stable_tuple(self.deployment_profiles):
            errors.append("deployment_profiles are required")
        if self.min_ram_mb < 1:
            errors.append("min_ram_mb must be >= 1")
        if self.min_storage_gb < 1:
            errors.append("min_storage_gb must be >= 1")
        if self.max_corpus_chunks < 0:
            errors.append("max_corpus_chunks must be >= 0")
        if self.max_concurrent_users < 1:
            errors.append("max_concurrent_users must be >= 1")
        if self.power_class not in {"LOW", "MEDIUM", "HIGH"}:
            errors.append("power_class must be LOW, MEDIUM or HIGH")
        if not 1 <= self.operational_complexity <= 5:
            errors.append("operational_complexity must be in [1,5]")
        if not self.lifecycle_state.strip():
            errors.append("lifecycle_state is required")
        if not self.evidence_state.strip():
            errors.append("evidence_state is required")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class StorageSelectionPolicy:
    policy_id: str
    version: str
    eligible_lifecycle_states: tuple[str, ...] = ("QUALIFIED", "RELEASED")
    required_evidence_state: str = "QUALIFIED"
    require_exact_brain_class: bool = True
    require_exact_deployment_profile: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("policy version is required")
        if not _stable_tuple(self.eligible_lifecycle_states):
            errors.append("eligible_lifecycle_states are required")
        if not self.required_evidence_state.strip():
            errors.append("required_evidence_state is required")
        if not self.require_exact_brain_class:
            errors.append("reference v1 requires exact brain class")
        if not self.require_exact_deployment_profile:
            errors.append("reference v1 requires exact deployment profile")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class RejectedStorageAlternative:
    profile_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StorageSelectionDecision:
    status: str
    selected_profile_id: str | None
    selection_reasons: tuple[str, ...]
    rejected_alternatives: tuple[RejectedStorageAlternative, ...]
    decision_id: str
    decision_hash: str


class DeterministicStorageProfileSelector:
    @staticmethod
    def _evaluate(
        request: StorageSelectionRequest,
        profile: StorageProfileDescriptor,
        policy: StorageSelectionPolicy,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if profile.lifecycle_state not in _stable_tuple(policy.eligible_lifecycle_states):
            reasons.append("lifecycle_state_not_eligible")
        if profile.evidence_state != policy.required_evidence_state:
            reasons.append("evidence_not_qualified")
        if (
            policy.require_exact_brain_class
            and request.brain_class not in _stable_tuple(profile.supported_brain_classes)
        ):
            reasons.append("brain_class_mismatch")
        if (
            policy.require_exact_deployment_profile
            and request.deployment_profile not in _stable_tuple(profile.deployment_profiles)
        ):
            reasons.append("deployment_profile_mismatch")
        missing = set(_stable_tuple(request.required_capabilities)) - set(
            _stable_tuple(profile.capabilities)
        )
        if missing:
            reasons.append("missing_capabilities:" + ",".join(sorted(missing)))
        if request.corpus_chunks > profile.max_corpus_chunks:
            reasons.append("corpus_envelope_exceeded")
        if request.concurrent_users > profile.max_concurrent_users:
            reasons.append("concurrency_envelope_exceeded")
        if request.max_ram_mb is not None and profile.min_ram_mb > request.max_ram_mb:
            reasons.append("ram_ceiling_exceeded")
        if (
            request.max_storage_gb is not None
            and profile.min_storage_gb > request.max_storage_gb
        ):
            reasons.append("storage_ceiling_exceeded")
        if request.offline_required and not profile.supports_offline:
            reasons.append("offline_required")
        if request.high_availability_required and not profile.supports_ha:
            reasons.append("ha_required")
        if request.high_assurance_required and not profile.supports_high_assurance:
            reasons.append("high_assurance_required")
        if request.power_constrained and profile.power_class != "LOW":
            reasons.append("low_power_required")
        return tuple(sorted(reasons))

    @staticmethod
    def _decision(
        request: StorageSelectionRequest,
        policy: StorageSelectionPolicy,
        *,
        status: str,
        selected: StorageProfileDescriptor | None,
        selection_reasons: tuple[str, ...],
        rejected: tuple[RejectedStorageAlternative, ...],
        eligible_ids: tuple[str, ...],
    ) -> StorageSelectionDecision:
        payload = {
            "request": {
                "request_id": request.request_id,
                "brain_class": request.brain_class,
                "deployment_profile": request.deployment_profile,
                "required_capabilities": _stable_tuple(request.required_capabilities),
                "corpus_chunks": request.corpus_chunks,
                "concurrent_users": request.concurrent_users,
                "target_p95_ms": request.target_p95_ms,
                "max_ram_mb": request.max_ram_mb,
                "max_storage_gb": request.max_storage_gb,
                "offline_required": request.offline_required,
                "high_availability_required": request.high_availability_required,
                "high_assurance_required": request.high_assurance_required,
                "power_constrained": request.power_constrained,
            },
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "status": status,
            "selected_profile_id": None if selected is None else selected.profile_id,
            "eligible_ids": tuple(sorted(eligible_ids)),
            "selection_reasons": tuple(sorted(selection_reasons)),
            "rejected": tuple(
                (item.profile_id, tuple(sorted(item.reasons)))
                for item in sorted(rejected, key=lambda item: item.profile_id)
            ),
        }
        digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return StorageSelectionDecision(
            status=status,
            selected_profile_id=None if selected is None else selected.profile_id,
            selection_reasons=tuple(selection_reasons),
            rejected_alternatives=tuple(sorted(rejected, key=lambda item: item.profile_id)),
            decision_id=f"STORAGE-{digest[:16]}",
            decision_hash=digest,
        )

    def select(
        self,
        request: StorageSelectionRequest,
        candidates: tuple[StorageProfileDescriptor, ...],
        policy: StorageSelectionPolicy,
    ) -> StorageSelectionDecision:
        validation = list(request.validate()) + list(policy.validate())
        for profile in candidates:
            validation.extend(
                f"{profile.profile_id}: {error}" for error in profile.validate()
            )
        if validation:
            return self._decision(
                request,
                policy,
                status="REJECTED",
                selected=None,
                selection_reasons=tuple(validation),
                rejected=(),
                eligible_ids=(),
            )

        eligible: list[StorageProfileDescriptor] = []
        rejected: list[RejectedStorageAlternative] = []
        for profile in sorted(candidates, key=lambda item: item.profile_id):
            reasons = self._evaluate(request, profile, policy)
            if reasons:
                rejected.append(RejectedStorageAlternative(profile.profile_id, reasons))
            else:
                eligible.append(profile)

        if not eligible:
            return self._decision(
                request,
                policy,
                status="NO_MATCH",
                selected=None,
                selection_reasons=("no profile satisfies all hard constraints",),
                rejected=tuple(rejected),
                eligible_ids=(),
            )

        def rank(profile: StorageProfileDescriptor) -> tuple[int, int, int]:
            return (
                profile.operational_complexity,
                profile.min_ram_mb,
                profile.min_storage_gb,
            )

        ranked = sorted(eligible, key=lambda item: (rank(item), item.profile_id))
        best_rank = rank(ranked[0])
        best = tuple(item for item in ranked if rank(item) == best_rank)

        if len(best) != 1:
            return self._decision(
                request,
                policy,
                status="AMBIGUOUS",
                selected=None,
                selection_reasons=("multiple profiles have equal minimal sufficient rank",),
                rejected=tuple(rejected),
                eligible_ids=tuple(item.profile_id for item in eligible),
            )

        selected = best[0]
        reasons = (
            f"brain_class={request.brain_class} supported",
            f"deployment_profile={request.deployment_profile} supported",
            "all required capabilities satisfied",
            "all resource/security/availability hard constraints satisfied",
            f"minimal operational_complexity={selected.operational_complexity}",
            f"declared min_ram_mb={selected.min_ram_mb}",
            f"declared min_storage_gb={selected.min_storage_gb}",
            "selection uses qualified profile envelope, not vendor preference",
        )
        return self._decision(
            request,
            policy,
            status="SELECTED",
            selected=selected,
            selection_reasons=reasons,
            rejected=tuple(rejected),
            eligible_ids=tuple(item.profile_id for item in eligible),
        )
