from __future__ import annotations

from dataclasses import dataclass


STORAGE_CLASSES = {
    "METADATA","STATE","VECTOR","OBJECT","GRAPH",
    "WORM_AUDIT","CACHE","SECRET","BACKUP","EVIDENCE",
}

NETWORK_ZONES = {
    "INGRESS","EGRESS","AGENT","MODEL","TOOL","DATA","MANAGEMENT","SANDBOX",
}


@dataclass(frozen=True)
class ApiPolicy:
    version: str
    auth_required: bool
    idempotency_required: bool
    breaking_change: bool
    deprecation_notice_days: int


def validate_api_policy(policy: ApiPolicy) -> bool:
    if not policy.version:
        return False
    if not policy.auth_required:
        return False
    if policy.breaking_change and policy.deprecation_notice_days <= 0:
        return False
    return True


@dataclass(frozen=True)
class StorageBinding:
    logical_class: str
    backend: str
    encrypted: bool


def validate_storage(binding: StorageBinding) -> bool:
    if binding.logical_class not in STORAGE_CLASSES:
        return False
    if binding.logical_class in {"SECRET","BACKUP","EVIDENCE","WORM_AUDIT"} and not binding.encrypted:
        return False
    return bool(binding.backend)


@dataclass(frozen=True)
class NetworkPolicy:
    zone: str
    default_action: str
    allowed_destinations: tuple[str, ...]


def validate_network(policy: NetworkPolicy) -> bool:
    if policy.zone not in NETWORK_ZONES:
        return False
    if policy.default_action != "DENY":
        return False
    return True


@dataclass(frozen=True)
class RecoveryPolicy:
    rpo_minutes: int
    rto_minutes: int
    restore_tested: bool


def validate_recovery(policy: RecoveryPolicy) -> bool:
    return (
        policy.rpo_minutes >= 0
        and policy.rto_minutes > 0
        and policy.restore_tested
    )


@dataclass(frozen=True)
class SupplyChainArtifact:
    name: str
    source_hash: str
    sbom_present: bool
    signature_verified: bool
    vulnerability_status: str


def validate_supply_chain(artifact: SupplyChainArtifact) -> bool:
    if len(artifact.source_hash) != 64:
        return False
    if not artifact.sbom_present or not artifact.signature_verified:
        return False
    return artifact.vulnerability_status == "PASS"


@dataclass(frozen=True)
class LicenseRecord:
    component: str
    license_id: str
    use_allowed: bool
    redistribution_allowed: bool
    attribution_required: bool


def validate_license(record: LicenseRecord) -> bool:
    return bool(record.component and record.license_id and record.use_allowed)


@dataclass(frozen=True)
class PrivacyRule:
    classification: str
    remote_model_allowed: bool
    retention_days: int


def validate_privacy(rule: PrivacyRule) -> bool:
    if rule.retention_days < 0:
        return False
    if rule.classification in {"PII","CREDENTIAL","SECRET-LIKE","RESTRICTED"} and rule.remote_model_allowed:
        return False
    return True


@dataclass(frozen=True)
class RetentionRule:
    artifact_type: str
    retention_days: int
    legal_hold: bool


def deletion_allowed(rule: RetentionRule, age_days: int) -> bool:
    if rule.legal_hold:
        return False
    return age_days >= rule.retention_days
