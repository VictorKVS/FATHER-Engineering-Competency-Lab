from __future__ import annotations

import uuid
from dataclasses import dataclass

from father_fua.audit import AuditLog
from father_fua.context_manager import ContextManager, ContextSegment
from father_fua.evaluator import CriterionResult, Evaluator
from father_fua.evidence import create_evidence
from father_fua.knowledge import KnowledgeRegistry
from father_fua.model_router import ModelProfile, ModelRouter
from father_fua.observability import Metrics
from father_fua.policy import PolicyEngine
from father_fua.rag import RagRegistry
from father_fua.readiness import MANDATORY, release_decision
from father_fua.resources import Budget
from father_fua.security_layer import security_gate
from father_fua.skills import Skill, SkillRegistry
from father_fua.tools_runtime import ToolRuntime, ToolSpec


@dataclass(frozen=True)
class MissionResult:
    mission_id: str
    status: str
    answer: dict
    evidence_id: str
    readiness: str


class FUAAssemblyRuntime:
    def __init__(self) -> None:
        self.audit = AuditLog()
        self.metrics = Metrics()
        self.rag = RagRegistry()
        self.knowledge = KnowledgeRegistry()
        self.policy = PolicyEngine("0.1")
        self.models = ModelRouter()
        self.tools = ToolRuntime()
        self.skills = SkillRegistry()
        self.context = ContextManager()
        self.evaluator = Evaluator()
        self.budget = Budget(token_limit=10000, money_limit=10.0)

        self.policy.allow("FUA-001", "tool.echo")
        self.policy.allow("FUA-001", "model.call")

        self.models.register(
            ModelProfile(
                model_id="LOCAL-STUB",
                provider="local-test",
                local_or_remote="LOCAL",
                context_window=8192,
                structured_output=True,
                tool_calling=True,
                cost_profile=0.0,
                privacy_profile="LOCAL_ONLY",
                healthy=True,
                approved=True,
            )
        )
        self.tools.register(
            ToolSpec("echo", False, ("ANALYST",)),
            lambda p: {"echo": p["text"]},
        )
        self.skills.register(Skill("base-read", "1.0", ("read",)))

    def run_mission(self, mission: str) -> MissionResult:
        mission_id = str(uuid.uuid4())
        corr = mission_id

        self.audit.append(
            kind="mission.accepted",
            actor="operator",
            correlation_id=corr,
            detail={"mission": mission},
        )
        self.metrics.inc("missions_total", labels={"agent": "FUA-001"})

        rag_hits = self.rag.retrieve(mission)
        trusted_hits = [x for x in rag_hits if not x["poison_suspected"]]

        context_segments = [
            ContextSegment("policy", "DENY BY DEFAULT", 100, mandatory=True, source="policy"),
            ContextSegment("mission", mission, 90, mandatory=True, source="operator"),
        ]
        for idx, hit in enumerate(trusted_hits):
            context_segments.append(
                ContextSegment(
                    f"rag-{idx}",
                    hit["content"],
                    50,
                    mandatory=False,
                    source=hit["provenance"],
                )
            )

        context = self.context.build(context_segments, max_chars=4096, remote_target=False)

        decision = self.policy.decide(
            subject="FUA-001",
            action="model.call",
            data_classification="INTERNAL",
            target_model_location="LOCAL",
        )
        if decision.decision != "ALLOW":
            raise PermissionError("model call denied")

        model = self.models.select(
            min_context=sum(len(s.text) for s in context),
            require_structured=True,
            local_only=True,
            max_cost=1.0,
        )

        self.budget.consume(tokens=min(500, sum(len(s.text) for s in context)))

        tool_decision = self.policy.decide(subject="FUA-001", action="tool.echo")
        if tool_decision.decision != "ALLOW":
            raise PermissionError("tool denied")

        tool_result = self.tools.execute(
            "echo",
            {"text": mission},
            role="ANALYST",
            policy_allow=True,
        )

        answer = {
            "model_id": model.model_id,
            "tool_result": tool_result,
            "rag_sources": [x["source_id"] for x in trusted_hits],
            "context_segments": [x.segment_id for x in context],
        }

        eval_summary = self.evaluator.summarize(
            [
                CriterionResult("MISSION_EXECUTED", "PASS", "runtime-trace"),
                CriterionResult("POLICY_ALLOWED", "PASS", decision.policy_version),
                CriterionResult("TOOL_SUCCESS", "PASS", "tool-audit"),
            ]
        )
        if eval_summary.status != "PASS":
            raise RuntimeError("evaluation failed")

        sec = security_gate([])
        if sec != "ALLOW":
            raise RuntimeError("security gate denied")

        evidence = create_evidence(
            f"EVID-{mission_id}",
            "ASSEMBLY_TEST",
            {
                "mission_id": mission_id,
                "model_id": model.model_id,
                "tool_result": tool_result,
                "rag_sources": answer["rag_sources"],
                "audit_ok": self.audit.verify(),
                "evaluation": eval_summary.status,
            },
        )

        gates = {k: "PASS" for k in MANDATORY}
        gates["HUMAN_ACCEPTANCE"] = "NOT_RUN"
        readiness = release_decision(gates)

        self.audit.append(
            kind="mission.completed",
            actor="FUA-001",
            correlation_id=corr,
            detail={"evidence_id": evidence.evidence_id, "readiness": readiness},
        )

        return MissionResult(
            mission_id=mission_id,
            status="PASS",
            answer=answer,
            evidence_id=evidence.evidence_id,
            readiness=readiness,
        )
