from __future__ import annotations

from dataclasses import dataclass

from father.factory.domain_pack import DomainPack
from father.factory.requirement_planner import CustomerRequirement


@dataclass(frozen=True, slots=True)
class ReferenceProductSpec:
    product_id: str
    version: str
    requirement: CustomerRequirement
    domain_pack: DomainPack


def osint_knowledge_spec() -> ReferenceProductSpec:
    return ReferenceProductSpec(
        product_id="FTH-PRODUCT-OSINT-KNOWLEDGE-001",
        version="0.1.0",
        requirement=CustomerRequirement(
            requirement_id="REQ-OSINT-KNOWLEDGE-001",
            title="OSINT knowledge analyst",
            needs=frozenset({
                "analyze_documents",
                "create_report",
                "run_workflow",
                "trace_decisions",
            }),
            required_permissions=frozenset({"execute:analysis", "read:evidence"}),
            metadata={"agent_id": "father-osint-knowledge-agent"},
        ),
        domain_pack=DomainPack(
            domain_pack_id="DP-OSINT-001",
            version="0.1.0",
            domain="osint",
            capabilities=frozenset({"decision.trace"}),
            knowledge_sources=("OSINT sources",),
            policies=("source_provenance_required", "unsupported_claims_unverified"),
        ),
    )


def security_kii_spec() -> ReferenceProductSpec:
    return ReferenceProductSpec(
        product_id="FTH-PRODUCT-SECURITY-KII-001",
        version="0.1.0",
        requirement=CustomerRequirement(
            requirement_id="REQ-SECURITY-KII-001",
            title="Security and KII analyst",
            needs=frozenset({
                "analyze_documents",
                "create_report",
                "enforce_policy",
                "trace_decisions",
                "run_workflow",
            }),
            required_permissions=frozenset({
                "execute:analysis",
                "read:evidence",
                "propose:decision",
            }),
            approval_required_for=frozenset({"create_report"}),
            metadata={"agent_id": "father-security-kii-agent"},
        ),
        domain_pack=DomainPack(
            domain_pack_id="DP-SECURITY-KII-001",
            version="0.1.0",
            domain="information_security_kii",
            capabilities=frozenset({"policy.enforce", "decision.trace"}),
            knowledge_sources=("SECGRAPH", "normative_requirements"),
            policies=(
                "authorization_before_decision",
                "normative_reference_required",
                "human_approval_for_final_decision",
            ),
        ),
    )
