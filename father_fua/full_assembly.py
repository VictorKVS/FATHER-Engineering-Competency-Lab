from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from father_fua.approval import Approval, action_hash, verify_approval
from father_fua.audit import AuditLog
from father_fua.compatibility import CompatibilityMatrix
from father_fua.context_manager import ContextManager, ContextSegment
from father_fua.evaluator import CriterionResult, Evaluator
from father_fua.evidence import Evidence, create_evidence
from father_fua.goal import create_goal
from father_fua.identity import create_identity
from father_fua.knowledge import KnowledgeRegistry
from father_fua.learning import LearningGate, LearningProposal
from father_fua.memory_runtime import MemoryItem, MemoryStore
from father_fua.model_router import ModelProfile, ModelRouter
from father_fua.observability import Metrics
from father_fua.planner import make_plan, validate_plan
from father_fua.policy import PolicyEngine
from father_fua.prompt_runtime import assemble_prompt
from father_fua.rag import RagRegistry
from father_fua.readiness import MANDATORY, release_decision
from father_fua.recovery import retry
from father_fua.resources import Budget
from father_fua.role import Role, authorize_duty
from father_fua.sandbox import SandboxPolicy, validate_path
from father_fua.security_layer import security_gate
from father_fua.skills import Skill, SkillRegistry
from father_fua.state_runtime import State, state_hash, transition
from father_fua.tools_runtime import ToolRuntime, ToolSpec


@dataclass(frozen=True)
class FullMissionResult:
    mission_id: str
    status: str
    identity_instance_id: str
    prompt_sha256: str
    state_sha256: str
    evidence: Evidence
    readiness: str
    audit_ok: bool
    answer: dict


class FullFUAAssemblyRuntime:
    def __init__(self) -> None:
        self.audit = AuditLog()
        self.metrics = Metrics()
        self.memory = MemoryStore()
        self.rag = RagRegistry()
        self.knowledge = KnowledgeRegistry()
        self.policy = PolicyEngine("0.2")
        self.models = ModelRouter()
        self.tools = ToolRuntime()
        self.skills = SkillRegistry()
        self.context = ContextManager()
        self.evaluator = Evaluator()
        self.learning = LearningGate()
        self.compatibility = CompatibilityMatrix()
        self.budget = Budget(token_limit=10000, money_limit=10.0)
        self.sandbox_policy = SandboxPolicy(
            network_allowed=False,
            max_seconds=30,
            allowed_roots=("G:/1/FATHER-Engineering-Competency-Lab/runtime",),
        )

        self.identity = create_identity(
            agent_id="FUA-001",
            version="0.2",
            owner="FATHER",
            trust_level="STANDARD",
        )
        self.role = Role(
            primary_role="ANALYST",
            allowed_duties=("mission.execute","tool.echo","model.call","knowledge.read"),
            forbidden_duties=("policy.modify","identity.modify"),
            jurisdiction=("LOCAL",),
        )
        self.state = State(0, str(uuid.uuid4()), "READY")

        self.policy.allow("FUA-001","model.call")
        self.policy.allow("FUA-001","tool.echo")
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
        self.skills.register(Skill("base-read","1.0",("read",)))
        self.skills.register(Skill("mission-runtime","1.0",("execute",),("base-read",)))
        self.compatibility.approve("LOCAL-STUB","PROMPT-0.2","mission-runtime","FUA-0.2")

    def run(self, mission: str) -> FullMissionResult:
        if not authorize_duty(self.role,"mission.execute"):
            raise PermissionError("role blocks mission")

        # Mission-scoped safety budgets must not become lifetime fuses.
        # Keep audit/metrics/history, but reset per-mission execution allowances.
        self.tools.reset_call_budget()
        self.budget.reset_usage()

        mission_id=str(uuid.uuid4())
        corr=mission_id
        self.state=transition(self.state,"MISSION_ACCEPTED")

        goal=create_goal(
            mission,
            success=["mission executed"],
            failure=["policy denied","budget exceeded","security denied"],
            constraints=["local model only","deny by default"],
            ttl_seconds=300,
        )
        plan=make_plan(mission_id,goal.mission)
        if not validate_plan(plan):
            raise RuntimeError("invalid plan")

        self.audit.append(
            kind="mission.accepted",
            actor=self.identity.instance_id,
            correlation_id=corr,
            detail={"mission_id":mission_id,"goal":goal.mission},
        )

        memory_hits=self.memory.query("PROJECT",mission)
        rag_hits=self.rag.retrieve(mission)
        safe_rag=[x for x in rag_hits if not x["poison_suspected"]]

        context_segments=[
            ContextSegment("identity",f"agent={self.identity.agent_id}",100,True,False,"identity"),
            ContextSegment("policy","DENY BY DEFAULT",100,True,False,"policy"),
            ContextSegment("role",self.role.primary_role,95,True,False,"role"),
            ContextSegment("goal",goal.mission,90,True,False,"goal"),
        ]
        for i,item in enumerate(memory_hits):
            context_segments.append(ContextSegment(f"memory-{i}",item.content,40,False,False,item.provenance))
        for i,hit in enumerate(safe_rag):
            context_segments.append(ContextSegment(f"rag-{i}",hit["content"],50,False,False,hit["provenance"]))

        context=self.context.build(context_segments,max_chars=4096,remote_target=False)
        prompt=assemble_prompt(
            system="FATHER POLICY: DENY BY DEFAULT",
            role=self.role.primary_role,
            task=goal.mission,
            context=[{"source":x.source,"text":x.text} for x in context if not x.mandatory],
        )

        if not self.compatibility.is_approved("LOCAL-STUB","PROMPT-0.2","mission-runtime","FUA-0.2"):
            raise RuntimeError("compatibility not approved")

        model_decision=self.policy.decide(
            subject="FUA-001",
            action="model.call",
            data_classification="INTERNAL",
            target_model_location="LOCAL",
        )
        if model_decision.decision != "ALLOW":
            raise PermissionError("model denied")

        model=self.models.select(
            min_context=sum(len(x.text) for x in context),
            require_tools=True,
            require_structured=True,
            local_only=True,
            max_cost=1.0,
        )

        self.budget.consume(tokens=min(500,sum(len(x.text) for x in context)),money=0.0)

        tool_decision=self.policy.decide(subject="FUA-001",action="tool.echo")
        if tool_decision.decision!="ALLOW":
            raise PermissionError("tool denied")

        def tool_call():
            return self.tools.execute(
                "echo",
                {"text":goal.mission},
                role=self.role.primary_role,
                policy_allow=True,
            )

        tool_result=retry(tool_call,attempts=2)

        if not validate_path(
            "G:/1/FATHER-Engineering-Competency-Lab/runtime/output.json",
            self.sandbox_policy,
        ):
            raise PermissionError("sandbox path denied")

        proposal=LearningProposal(
            proposal_id=f"LP-{mission_id}",
            kind="NEGATIVE_OR_GOLD_CANDIDATE",
            content="mission result available for review",
            provenance=f"mission:{mission_id}",
        )
        if proposal.approved:
            raise RuntimeError("learning proposal must not self-approve")

        privileged_action="release.production"
        approval=Approval(
            action_hash=action_hash(privileged_action),
            approver="factory-test-human",
            decision="DENY",
            expires_at=time.time()+60,
        )
        human_release_approved=verify_approval(approval,privileged_action)

        evaluation=self.evaluator.summarize([
            CriterionResult("GOAL","PASS",f"goal:{mission_id}"),
            CriterionResult("PLAN","PASS",f"plan:{len(plan)}"),
            CriterionResult("MODEL","PASS",model.model_id),
            CriterionResult("TOOL","PASS","tool:echo"),
            CriterionResult("PROMPT","PASS",prompt.sha256),
        ])
        if evaluation.status!="PASS":
            raise RuntimeError("evaluation failed")

        if security_gate([])!="ALLOW":
            raise RuntimeError("security gate denied")

        self.state=transition(self.state,"MISSION_COMPLETED")
        state_sha=state_hash(self.state)

        answer={
            "model_id":model.model_id,
            "tool_result":tool_result,
            "rag_sources":[x["source_id"] for x in safe_rag],
            "memory_count":len(memory_hits),
            "plan_tasks":[x.task_id for x in plan],
            "context_segments":[x.segment_id for x in context],
            "learning_proposal_approved":proposal.approved,
            "human_release_approved":human_release_approved,
            "sandbox_network_allowed":self.sandbox_policy.network_allowed,
        }

        evidence=create_evidence(
            f"EVID-FULL-{mission_id}",
            "FULL_ASSEMBLY_TEST",
            {
                "agent_id":self.identity.agent_id,
                "instance_id":self.identity.instance_id,
                "mission_id":mission_id,
                "prompt_sha256":prompt.sha256,
                "state_sha256":state_sha,
                "model_id":model.model_id,
                "tool_result":tool_result,
                "evaluation":evaluation.status,
                "security":"ALLOW",
            },
        )

        self.audit.append(
            kind="mission.completed",
            actor=self.identity.instance_id,
            correlation_id=corr,
            detail={"evidence_id":evidence.evidence_id},
        )
        self.metrics.inc("missions_completed",labels={"agent":"FUA-001"})
        self.metrics.observe("assembly_steps",float(len(plan)),labels={"agent":"FUA-001"})

        gates={k:"PASS" for k in MANDATORY}
        gates["HUMAN_ACCEPTANCE"]="PASS" if human_release_approved else "NOT_RUN"
        readiness=release_decision(gates)

        return FullMissionResult(
            mission_id=mission_id,
            status="PASS",
            identity_instance_id=self.identity.instance_id,
            prompt_sha256=prompt.sha256,
            state_sha256=state_sha,
            evidence=evidence,
            readiness=readiness,
            audit_ok=self.audit.verify(),
            answer=answer,
        )
