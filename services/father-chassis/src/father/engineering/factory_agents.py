from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class KnowledgeBaseContract:
    kb_id: str
    purpose: str
    required_source_classes: tuple[str, ...]
    required_entities: tuple[str, ...]
    required_relationships: tuple[str, ...]
    required_metadata: tuple[str, ...] = (
        "source_id",
        "title",
        "version",
        "effective_date",
        "locator",
        "content_hash",
        "provenance",
    )
    freshness_policy: str = "versioned"
    qualification_policy: str = "source provenance + retrieval evidence"


@dataclass(frozen=True, slots=True)
class AgentOutputContract:
    artifact_type: str
    required_fields: tuple[str, ...]
    acceptance_metrics: tuple[str, ...]
    evidence_required: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FactoryAgentContract:
    agent_id: str
    role_name: str
    mission: str
    upstream_inputs: tuple[str, ...]
    downstream_outputs: tuple[AgentOutputContract, ...]
    allowed_decisions: tuple[str, ...]
    forbidden_decisions: tuple[str, ...]
    mandatory_checks: tuple[str, ...]
    knowledge_bases: tuple[KnowledgeBaseContract, ...]
    escalation_targets: tuple[str, ...]
    required_tools: tuple[str, ...] = ()
    quality_metrics: tuple[str, ...] = ()
    contract_hash: str = ""

    def __post_init__(self) -> None:
        if not self.agent_id.strip():
            raise ValueError("agent_id is required")
        if not self.role_name.strip():
            raise ValueError("role_name is required")
        if not self.mission.strip():
            raise ValueError("mission is required")
        if not self.upstream_inputs:
            raise ValueError("upstream_inputs are required")
        if not self.downstream_outputs:
            raise ValueError("downstream_outputs are required")
        if not self.knowledge_bases:
            raise ValueError("knowledge_bases are required")

        if not self.contract_hash:
            payload = {
                "agent_id": self.agent_id,
                "role_name": self.role_name,
                "mission": self.mission,
                "upstream_inputs": self.upstream_inputs,
                "downstream_outputs": [asdict(x) for x in self.downstream_outputs],
                "allowed_decisions": self.allowed_decisions,
                "forbidden_decisions": self.forbidden_decisions,
                "mandatory_checks": self.mandatory_checks,
                "knowledge_bases": [asdict(x) for x in self.knowledge_bases],
                "escalation_targets": self.escalation_targets,
                "required_tools": self.required_tools,
                "quality_metrics": self.quality_metrics,
            }
            object.__setattr__(
                self,
                "contract_hash",
                sha256(_canonical(payload).encode("utf-8")).hexdigest(),
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FactoryAgentCatalog:
    agents: tuple[FactoryAgentContract, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        ids = {agent.agent_id for agent in self.agents}
        if len(ids) != len(self.agents):
            errors.append("duplicate agent_id")
        for agent in self.agents:
            for target in agent.escalation_targets:
                if target not in ids and target != "HUMAN_APPROVAL":
                    errors.append(f"{agent.agent_id}: unknown escalation target {target}")
        return errors

    def by_id(self, agent_id: str) -> FactoryAgentContract:
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        raise KeyError(agent_id)


def business_analyst_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-BUSINESS-ANALYSIS",
        purpose="Business goals, value, processes, actors, KPIs, constraints and economics.",
        required_source_classes=(
            "business_strategy",
            "process_regulation",
            "stakeholder_interview",
            "kpi_catalog",
            "service_catalog",
            "financial_model",
        ),
        required_entities=(
            "business_goal",
            "stakeholder",
            "process",
            "process_step",
            "actor",
            "input",
            "output",
            "kpi",
            "constraint",
            "business_rule",
        ),
        required_relationships=(
            "goal_drives_process",
            "actor_performs_step",
            "step_consumes_input",
            "step_produces_output",
            "kpi_measures_goal",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-BUSINESS-ANALYST",
        role_name="Senior Business Analyst",
        mission="Translate business intent into measurable, optimized and approved business-process requirements.",
        upstream_inputs=("customer_request", "business_context", "stakeholder_constraints"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="BusinessProcessSpec",
                required_fields=("goal", "inputs", "outputs", "actors", "success_metrics"),
                acceptance_metrics=("goal_coverage", "stakeholder_coverage", "metric_completeness"),
                evidence_required=("source_links", "decision_log"),
            ),
        ),
        allowed_decisions=(
            "clarify_business_goal",
            "decompose_process",
            "identify_kpis",
            "propose_process_optimization",
        ),
        forbidden_decisions=(
            "choose_software_architecture",
            "invent_api_schema",
            "implement_code",
        ),
        mandatory_checks=(
            "business_value",
            "process_completeness",
            "stakeholder_conflicts",
            "measurable_success",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-SYSTEM-ANALYST", "HUMAN_APPROVAL"),
        required_tools=("process_modeler", "cost_value_analyzer"),
        quality_metrics=("business_goal_coverage", "process_completeness", "ambiguity_rate"),
    )


def system_analyst_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-SYSTEM-ANALYSIS",
        purpose="System requirements, state models, interfaces, data contracts and failure modes.",
        required_source_classes=(
            "business_process_spec",
            "requirements_standard",
            "interface_catalog",
            "data_dictionary",
            "failure_catalog",
            "nonfunctional_requirements",
        ),
        required_entities=(
            "system_requirement",
            "actor",
            "use_case",
            "state",
            "event",
            "data_entity",
            "interface",
            "constraint",
            "failure_mode",
        ),
        required_relationships=(
            "requirement_realizes_business_goal",
            "event_changes_state",
            "interface_transfers_entity",
            "failure_impacts_requirement",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-SYSTEM-ANALYST",
        role_name="Senior System Analyst",
        mission="Convert approved business process into complete and internally consistent system requirements.",
        upstream_inputs=("BusinessProcessSpec", "business_rules", "constraints"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="SystemAnalysisPackage",
                required_fields=("functional_requirements", "states", "events", "data", "interfaces", "failures"),
                acceptance_metrics=("requirements_coverage", "consistency", "ambiguity_rate"),
                evidence_required=("traceability_matrix", "conflict_log"),
            ),
        ),
        allowed_decisions=(
            "decompose_system_requirements",
            "define_states",
            "define_data_semantics",
            "identify_failure_modes",
            "detect_contradictions",
        ),
        forbidden_decisions=(
            "select_final_algorithm",
            "select_implementation_library",
            "write_production_code",
        ),
        mandatory_checks=(
            "requirement_traceability",
            "state_consistency",
            "data_completeness",
            "failure_coverage",
            "nonfunctional_requirements",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-ALGORITHM-ENGINEER", "FTH-AGENT-ARCHITECT", "HUMAN_APPROVAL"),
        required_tools=("requirements_graph", "state_model_checker"),
        quality_metrics=("requirements_coverage", "contradiction_rate", "unresolved_ambiguity_count"),
    )


def algorithm_engineer_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-ALGORITHMS",
        purpose="Algorithms, data structures, complexity, optimization, benchmark patterns and trade-offs.",
        required_source_classes=(
            "algorithm_reference",
            "benchmark",
            "research_paper",
            "performance_report",
            "architecture_pattern",
            "failure_case",
        ),
        required_entities=(
            "algorithm",
            "variant",
            "complexity",
            "quality_metric",
            "resource_metric",
            "constraint",
            "benchmark",
        ),
        required_relationships=(
            "variant_satisfies_constraint",
            "algorithm_has_complexity",
            "benchmark_measures_variant",
            "variant_trades_quality_for_cost",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-ALGORITHM-ENGINEER",
        role_name="Senior Algorithm Engineer",
        mission="Compare feasible solution algorithms and select the best justified option under project constraints.",
        upstream_inputs=("SystemAnalysisPackage", "business_metrics", "constraints"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="AlgorithmSpec",
                required_fields=("preconditions", "steps", "postconditions", "invariants", "complexity_limits"),
                acceptance_metrics=("quality", "latency", "resource_cost", "scalability", "maintainability"),
                evidence_required=("alternatives_matrix", "benchmark_or_reference", "decision_rationale"),
            ),
        ),
        allowed_decisions=(
            "enumerate_algorithm_options",
            "benchmark_options",
            "select_algorithm",
            "define_complexity_limits",
        ),
        forbidden_decisions=(
            "change_business_goal",
            "invent_system_requirement",
            "choose_code_level_implementation_detail",
        ),
        mandatory_checks=(
            "alternative_analysis",
            "complexity",
            "quality",
            "latency",
            "resource_usage",
            "failure_behavior",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-ARCHITECT", "FTH-AGENT-SYSTEM-ANALYST", "HUMAN_APPROVAL"),
        required_tools=("benchmark_runner", "complexity_estimator"),
        quality_metrics=("decision_evidence_score", "benchmark_coverage", "constraint_satisfaction"),
    )


def architect_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-ARCHITECTURE",
        purpose="Architecture patterns, integration contracts, distributed systems, AI architecture and quality attributes.",
        required_source_classes=(
            "architecture_standard",
            "adr",
            "reference_architecture",
            "integration_pattern",
            "security_architecture",
            "sizing_guide",
        ),
        required_entities=(
            "block",
            "interface",
            "state",
            "constant",
            "data_flow",
            "dependency",
            "quality_attribute",
            "security_boundary",
        ),
        required_relationships=(
            "block_calls_block",
            "interface_connects_blocks",
            "block_owns_state",
            "data_flows_through_interface",
            "dependency_impacts_availability",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-ARCHITECT",
        role_name="Principal / Solution Architect",
        mission="Transform approved system requirements and algorithm into explicit blocks, variables, interfaces, states and quality boundaries.",
        upstream_inputs=("SystemAnalysisPackage", "AlgorithmSpec", "platform_constraints"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="ArchitectureSpec",
                required_fields=("blocks", "interfaces", "states", "constants"),
                acceptance_metrics=("traceability", "cohesion", "coupling", "quality_attribute_coverage"),
                evidence_required=("architecture_diagram", "interface_contracts", "ADR"),
            ),
        ),
        allowed_decisions=(
            "define_blocks",
            "define_interfaces",
            "assign_state_ownership",
            "define_security_boundaries",
            "select_architecture_patterns",
        ),
        forbidden_decisions=(
            "silently_change_business_goal",
            "silently_change_approved_algorithm",
            "write_unreviewed_production_code",
        ),
        mandatory_checks=(
            "all_variables_declared",
            "all_interfaces_typed",
            "state_ownership_unique",
            "failure_boundaries",
            "security_boundaries",
            "scalability",
            "replaceability",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-SYSTEM-ANALYST", "FTH-AGENT-TEST-ARCHITECT", "HUMAN_APPROVAL"),
        required_tools=("architecture_graph", "dependency_analyzer", "sizing_calculator"),
        quality_metrics=("architecture_traceability", "interface_completeness", "replaceability_score"),
    )


def test_architect_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-TEST-ENGINEERING",
        purpose="Testing strategies, contract testing, performance, reliability, security and acceptance metrics.",
        required_source_classes=(
            "requirements",
            "architecture_spec",
            "algorithm_spec",
            "test_pattern",
            "incident_history",
            "slo_catalog",
        ),
        required_entities=(
            "criterion",
            "metric",
            "threshold",
            "test_case",
            "failure_mode",
            "resource_limit",
            "evidence_type",
        ),
        required_relationships=(
            "criterion_verifies_requirement",
            "test_covers_failure_mode",
            "metric_has_threshold",
            "evidence_proves_criterion",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-TEST-ARCHITECT",
        role_name="Senior Test Architect / QA",
        mission="Derive executable acceptance and failure contracts from approved algorithm and architecture before implementation.",
        upstream_inputs=("BusinessProcessSpec", "SystemAnalysisPackage", "AlgorithmSpec", "ArchitectureSpec"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="TestContract",
                required_fields=("criteria", "required_test_levels"),
                acceptance_metrics=("requirement_coverage", "failure_coverage", "metric_coverage"),
                evidence_required=("test_matrix", "acceptance_thresholds"),
            ),
        ),
        allowed_decisions=(
            "derive_test_cases",
            "define_acceptance_thresholds_from_requirements",
            "define_negative_tests",
            "define_resource_and_latency_checks",
        ),
        forbidden_decisions=(
            "change_architecture_to_make_test_pass",
            "weaken_business_requirement",
            "implement_feature_logic",
        ),
        mandatory_checks=(
            "happy_path",
            "negative_path",
            "boundary_conditions",
            "performance",
            "resource_usage",
            "security",
            "recovery",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-ARCHITECT", "FTH-AGENT-SYSTEM-ANALYST", "HUMAN_APPROVAL"),
        required_tools=("test_generator", "coverage_analyzer", "load_modeler"),
        quality_metrics=("requirements_coverage", "negative_case_coverage", "acceptance_clarity"),
    )


def senior_developer_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-SOFTWARE-ENGINEERING",
        purpose="Language, libraries, implementation patterns, code quality, performance and maintainability.",
        required_source_classes=(
            "language_reference",
            "library_documentation",
            "coding_standard",
            "design_pattern",
            "performance_guide",
            "security_guide",
        ),
        required_entities=(
            "language_feature",
            "library",
            "component",
            "pattern",
            "api",
            "resource_cost",
            "security_constraint",
        ),
        required_relationships=(
            "component_implements_interface",
            "library_provides_component",
            "pattern_improves_quality_attribute",
            "implementation_satisfies_contract",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-SENIOR-DEVELOPER",
        role_name="Senior Software Engineer",
        mission="Implement the approved DevelopmentPacket using the best code-level structures and components without changing system semantics.",
        upstream_inputs=("DevelopmentPacket",),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="ImplementationChange",
                required_fields=("source_changes", "tests", "commit_message", "traceability"),
                acceptance_metrics=("contract_compliance", "maintainability", "resource_efficiency"),
                evidence_required=("static_analysis", "unit_tests", "contract_tests", "diff"),
            ),
        ),
        allowed_decisions=(
            "choose_language_construct",
            "choose_internal_data_structure",
            "choose_approved-compatible_library",
            "refactor_internal_code",
            "optimize_performance_without_semantic_change",
        ),
        forbidden_decisions=(
            "invent_variable_semantics",
            "invent_api_field",
            "change_state_ownership",
            "change_approved_algorithm",
            "weaken_acceptance_threshold",
            "bypass_security_contract",
        ),
        mandatory_checks=(
            "development_packet_complete",
            "static_correctness",
            "interface_compliance",
            "resource_behavior",
            "backward_compatibility",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-ARCHITECT", "FTH-AGENT-ALGORITHM-ENGINEER", "FTH-AGENT-TEST-ARCHITECT"),
        required_tools=("code_editor", "static_analyzer", "dependency_inspector"),
        quality_metrics=("contract_compliance", "static_error_count", "maintainability", "performance"),
    )


def devsecops_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-DEVSECOPS",
        purpose="CI/CD, supply chain security, deployment, observability, infrastructure and recovery.",
        required_source_classes=(
            "ci_cd_reference",
            "container_reference",
            "kubernetes_reference",
            "security_standard",
            "supply_chain_standard",
            "runbook",
        ),
        required_entities=(
            "pipeline",
            "artifact",
            "image",
            "dependency",
            "sbom",
            "signature",
            "environment",
            "deployment",
            "rollback",
        ),
        required_relationships=(
            "pipeline_builds_artifact",
            "artifact_has_sbom",
            "deployment_uses_artifact",
            "rollback_restores_version",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-DEVSECOPS",
        role_name="Senior DevSecOps / SRE",
        mission="Build secure reproducible delivery, runtime operations, observability, recovery and supply-chain evidence.",
        upstream_inputs=("ImplementationChange", "ArchitectureSpec", "TestContract"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="DeliveryQualification",
                required_fields=("build", "deploy", "security", "observability", "rollback"),
                acceptance_metrics=("reproducibility", "availability", "security_gate_pass", "recovery_time"),
                evidence_required=("sbom", "scan_reports", "build_provenance", "runtime_metrics"),
            ),
        ),
        allowed_decisions=(
            "choose_pipeline_implementation",
            "choose_deployment_mechanism_within_architecture",
            "configure_observability",
            "optimize_runtime_resources",
        ),
        forbidden_decisions=(
            "change_product_semantics",
            "disable_security_gate",
            "silently_raise_resource_budget",
        ),
        mandatory_checks=(
            "reproducible_build",
            "dependency_integrity",
            "secret_scanning",
            "static_security",
            "sbom",
            "rollback",
            "health",
            "observability",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("FTH-AGENT-ARCHITECT", "FTH-AGENT-TEST-ARCHITECT", "HUMAN_APPROVAL"),
        required_tools=("ci_cd", "container_runtime", "security_scanners", "observability_stack"),
        quality_metrics=("build_reproducibility", "security_findings", "recovery_time", "resource_efficiency"),
    )


def qualification_auditor_contract() -> FactoryAgentContract:
    kb = KnowledgeBaseContract(
        kb_id="KB-QUALIFICATION-EVIDENCE",
        purpose="Qualification policy, evidence quality, provenance, traceability and competency.",
        required_source_classes=(
            "qualification_policy",
            "test_evidence",
            "security_evidence",
            "runtime_trace",
            "provenance_record",
            "competency_policy",
        ),
        required_entities=(
            "claim",
            "evidence",
            "criterion",
            "qualification",
            "subject",
            "provenance",
            "exception",
        ),
        required_relationships=(
            "evidence_supports_claim",
            "criterion_requires_evidence",
            "qualification_assesses_subject",
            "exception_blocks_qualification",
        ),
    )
    return FactoryAgentContract(
        agent_id="FTH-AGENT-QUALIFICATION-AUDITOR",
        role_name="Qualification / Evidence Auditor",
        mission="Independently decide whether evidence proves the approved acceptance contract; never manufacture missing evidence.",
        upstream_inputs=("TestContract", "DeliveryQualification", "runtime_evidence", "provenance"),
        downstream_outputs=(
            AgentOutputContract(
                artifact_type="QualificationDecision",
                required_fields=("status", "criteria_results", "evidence_refs", "blocking_findings"),
                acceptance_metrics=("evidence_coverage", "traceability", "independence"),
                evidence_required=("qualification_record",),
            ),
        ),
        allowed_decisions=(
            "accept_evidence",
            "reject_evidence",
            "block_qualification",
            "request_missing_evidence",
        ),
        forbidden_decisions=(
            "invent_evidence",
            "waive_blocking_requirement_without_authority",
            "modify_product_to_make_it_pass",
        ),
        mandatory_checks=(
            "criterion_by_criterion_evidence",
            "hash_integrity",
            "source_provenance",
            "traceability",
            "blocking_findings",
        ),
        knowledge_bases=(kb,),
        escalation_targets=("HUMAN_APPROVAL",),
        required_tools=("evidence_ledger", "hash_verifier", "traceability_graph"),
        quality_metrics=("evidence_coverage", "false_pass_rate", "unresolved_blockers"),
    )


def build_factory_agent_catalog() -> FactoryAgentCatalog:
    catalog = FactoryAgentCatalog(
        agents=(
            business_analyst_contract(),
            system_analyst_contract(),
            algorithm_engineer_contract(),
            architect_contract(),
            test_architect_contract(),
            senior_developer_contract(),
            devsecops_contract(),
            qualification_auditor_contract(),
        )
    )
    errors = catalog.validate()
    if errors:
        raise ValueError("invalid factory agent catalog: " + "; ".join(errors))
    return catalog
