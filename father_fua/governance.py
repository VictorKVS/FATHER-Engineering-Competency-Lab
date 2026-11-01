from __future__ import annotations

from dataclasses import dataclass


DATA_CLASSES = {
    "PUBLIC","INTERNAL","CONFIDENTIAL","RESTRICTED",
    "SECRET-LIKE","PII","CREDENTIAL","SECURITY-SENSITIVE",
}

DEPLOYMENT_PROFILES = {
    "LOCAL_DEV","LOCAL_GPU","WORKSTATION","DOCKER",
    "KUBERNETES","CLOUD","AIR_GAPPED","EDGE",
}

AUTONOMY_LEVELS = {"L0","L1","L2","L3","L4","L5"}


@dataclass(frozen=True)
class DataAssetPolicy:
    data_type: str
    classification: str
    retention_days: int
    encrypted_at_rest: bool
    encrypted_in_transit: bool
    allowed_readers: tuple[str, ...]
    allowed_writers: tuple[str, ...]


def validate_data_policy(policy: DataAssetPolicy) -> bool:
    if policy.classification not in DATA_CLASSES:
        return False
    if policy.retention_days < 0:
        return False
    if policy.classification in {"RESTRICTED","SECRET-LIKE","PII","CREDENTIAL"}:
        if not policy.encrypted_at_rest or not policy.encrypted_in_transit:
            return False
    return True


@dataclass(frozen=True)
class DeploymentProfile:
    name: str
    network_mode: str
    remote_models_allowed: bool
    secrets_backend: str


def validate_deployment(profile: DeploymentProfile) -> bool:
    if profile.name not in DEPLOYMENT_PROFILES:
        return False
    if profile.name == "AIR_GAPPED" and profile.network_mode != "NONE":
        return False
    if profile.name == "AIR_GAPPED" and profile.remote_models_allowed:
        return False
    return bool(profile.secrets_backend)


@dataclass(frozen=True)
class ChangeRequest:
    component: str
    change_type: str
    requires_recertification: bool


RECERTIFY_TYPES = {"MODEL","PROMPT","KNOWLEDGE","POLICY","TOOL","SKILL","SECURITY_BASELINE"}


def validate_change(change: ChangeRequest) -> bool:
    if change.change_type in RECERTIFY_TYPES and not change.requires_recertification:
        return False
    return True


@dataclass(frozen=True)
class AgentTrust:
    agent_id: str
    authenticated: bool
    authorized_capabilities: tuple[str, ...]
    autonomy_level: str


def can_delegate(source: AgentTrust, target: AgentTrust, capability: str) -> bool:
    if source.autonomy_level not in AUTONOMY_LEVELS or target.autonomy_level not in AUTONOMY_LEVELS:
        return False
    if not source.authenticated or not target.authenticated:
        return False
    return capability in target.authorized_capabilities
