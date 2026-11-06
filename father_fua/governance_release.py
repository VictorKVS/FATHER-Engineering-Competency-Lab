from __future__ import annotations

from dataclasses import dataclass


AUTONOMY_LEVELS = {"L0","L1","L2","L3","L4","L5"}


@dataclass(frozen=True)
class DomainPack:
    pack_id: str
    has_role: bool
    has_prompts: bool
    has_knowledge: bool
    has_rag: bool
    has_skills: bool
    has_tools: bool
    has_policies: bool
    has_tests: bool
    has_evidence: bool


def validate_domain_pack(pack: DomainPack) -> bool:
    return all((
        pack.pack_id,
        pack.has_role,
        pack.has_prompts,
        pack.has_knowledge,
        pack.has_rag,
        pack.has_skills,
        pack.has_tools,
        pack.has_policies,
        pack.has_tests,
        pack.has_evidence,
    ))


@dataclass(frozen=True)
class AgentPackage:
    agent_id: str
    manifest_present: bool
    sbom_present: bool
    model_profile_present: bool
    prompt_pack_present: bool
    knowledge_pack_present: bool
    tool_pack_present: bool
    policy_pack_present: bool
    test_suite_present: bool
    evidence_present: bool
    signature_verified: bool


def validate_agent_package(pkg: AgentPackage) -> bool:
    return all((
        pkg.agent_id,
        pkg.manifest_present,
        pkg.sbom_present,
        pkg.model_profile_present,
        pkg.prompt_pack_present,
        pkg.knowledge_pack_present,
        pkg.tool_pack_present,
        pkg.policy_pack_present,
        pkg.test_suite_present,
        pkg.evidence_present,
        pkg.signature_verified,
    ))


@dataclass(frozen=True)
class SLO:
    availability: float
    p95_latency_ms: int
    max_error_rate: float
    min_tool_success_rate: float


def validate_slo(slo: SLO) -> bool:
    return (
        0 < slo.availability <= 1
        and slo.p95_latency_ms > 0
        and 0 <= slo.max_error_rate < 1
        and 0 < slo.min_tool_success_rate <= 1
    )


@dataclass(frozen=True)
class Capacity:
    cpu_cores: int
    ram_gb: int
    vram_gb: int
    storage_gb: int
    concurrent_jobs: int
    growth_margin_percent: int


def validate_capacity(c: Capacity) -> bool:
    return (
        c.cpu_cores > 0
        and c.ram_gb > 0
        and c.storage_gb > 0
        and c.concurrent_jobs > 0
        and 0 <= c.growth_margin_percent <= 500
    )


@dataclass
class FinOpsBudget:
    max_cost: float
    spent: float = 0.0

    def charge(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("negative charge")
        if self.spent + amount > self.max_cost:
            raise RuntimeError("budget exceeded")
        self.spent += amount


@dataclass(frozen=True)
class AutonomyPolicy:
    configured_level: str
    runtime_level: str


def validate_autonomy(policy: AutonomyPolicy) -> bool:
    if policy.configured_level not in AUTONOMY_LEVELS or policy.runtime_level not in AUTONOMY_LEVELS:
        return False
    configured=int(policy.configured_level[1:])
    runtime=int(policy.runtime_level[1:])
    return runtime <= configured


@dataclass(frozen=True)
class IncidentState:
    detected: bool
    contained: bool
    evidence_preserved: bool
    recovered: bool
    recertified: bool


def incident_closed(state: IncidentState) -> bool:
    return all((
        state.detected,
        state.contained,
        state.evidence_preserved,
        state.recovered,
        state.recertified,
    ))


@dataclass(frozen=True)
class DecommissionState:
    credentials_revoked: bool
    tools_disabled: bool
    tokens_invalidated: bool
    evidence_archived: bool
    runtime_removed: bool
    discovery_removed: bool


def decommission_complete(state: DecommissionState) -> bool:
    return all(state.__dict__.values())


DOD_GATES = (
    "BLOCKS_01_26",
    "TEST_BLOCKS",
    "POLYGON",
    "SECURITY",
    "COMPATIBILITY",
    "SBOM",
    "EVIDENCE",
    "BACKUP_RESTORE",
    "INCIDENT_RESPONSE",
    "SLO_COST",
    "REAL_SPECIALIZED_AGENT",
)


def definition_of_done(gates: dict[str,str]) -> str:
    return "PRODUCTION_READY" if all(gates.get(k)=="PASS" for k in DOD_GATES) else "DENIED"
