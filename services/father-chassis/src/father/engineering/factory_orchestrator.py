from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from father.engineering.factory_agents import FactoryAgentCatalog, build_factory_agent_catalog


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class StageArtifact:
    artifact_id: str
    artifact_type: str
    producer_agent_id: str
    payload: dict[str, Any]
    approved: bool
    evidence_refs: tuple[str, ...] = ()
    artifact_hash: str = ""

    def __post_init__(self) -> None:
        if not self.artifact_id.strip():
            raise ValueError("artifact_id is required")
        if not self.artifact_type.strip():
            raise ValueError("artifact_type is required")
        if not self.producer_agent_id.strip():
            raise ValueError("producer_agent_id is required")
        if not self.artifact_hash:
            payload = {
                "artifact_id": self.artifact_id,
                "artifact_type": self.artifact_type,
                "producer_agent_id": self.producer_agent_id,
                "payload": self.payload,
                "approved": self.approved,
                "evidence_refs": self.evidence_refs,
            }
            object.__setattr__(
                self,
                "artifact_hash",
                sha256(_canonical(payload).encode("utf-8")).hexdigest(),
            )


@dataclass(frozen=True, slots=True)
class StageDefinition:
    stage_id: str
    agent_id: str
    requires_artifact_types: tuple[str, ...]
    produces_artifact_type: str
    requires_approval: bool = True


@dataclass(frozen=True, slots=True)
class StageResult:
    stage_id: str
    agent_id: str
    status: str
    artifact: StageArtifact | None
    blocking_findings: tuple[str, ...] = ()


class FactoryEngineeringWorkflow:
    """Fail-closed role orchestration for engineering delivery."""

    def __init__(self, catalog: FactoryAgentCatalog | None = None) -> None:
        self.catalog = catalog or build_factory_agent_catalog()
        self.stages = (
            StageDefinition(
                "BUSINESS_ANALYSIS",
                "FTH-AGENT-BUSINESS-ANALYST",
                ("customer_request",),
                "BusinessProcessSpec",
            ),
            StageDefinition(
                "SYSTEM_ANALYSIS",
                "FTH-AGENT-SYSTEM-ANALYST",
                ("BusinessProcessSpec",),
                "SystemAnalysisPackage",
            ),
            StageDefinition(
                "ALGORITHM_SELECTION",
                "FTH-AGENT-ALGORITHM-ENGINEER",
                ("SystemAnalysisPackage",),
                "AlgorithmSpec",
            ),
            StageDefinition(
                "ARCHITECTURE",
                "FTH-AGENT-ARCHITECT",
                ("SystemAnalysisPackage", "AlgorithmSpec"),
                "ArchitectureSpec",
            ),
            StageDefinition(
                "TEST_ARCHITECTURE",
                "FTH-AGENT-TEST-ARCHITECT",
                ("BusinessProcessSpec", "SystemAnalysisPackage", "AlgorithmSpec", "ArchitectureSpec"),
                "TestContract",
            ),
            StageDefinition(
                "DEVELOPMENT_PACKET",
                "FTH-AGENT-ARCHITECT",
                ("BusinessProcessSpec", "AlgorithmSpec", "ArchitectureSpec", "TestContract"),
                "DevelopmentPacket",
            ),
            StageDefinition(
                "IMPLEMENTATION",
                "FTH-AGENT-SENIOR-DEVELOPER",
                ("DevelopmentPacket",),
                "ImplementationChange",
            ),
            StageDefinition(
                "DELIVERY",
                "FTH-AGENT-DEVSECOPS",
                ("ImplementationChange", "ArchitectureSpec", "TestContract"),
                "DeliveryQualification",
            ),
            StageDefinition(
                "QUALIFICATION",
                "FTH-AGENT-QUALIFICATION-AUDITOR",
                ("TestContract", "DeliveryQualification"),
                "QualificationDecision",
            ),
        )
        self._artifacts: dict[str, StageArtifact] = {}
        self._history: list[StageResult] = []

    def add_external_artifact(self, artifact: StageArtifact) -> None:
        if not artifact.approved:
            raise ValueError("external artifact must be approved")
        self._artifacts[artifact.artifact_type] = artifact

    def available_stage(self) -> StageDefinition | None:
        for stage in self.stages:
            if any(result.stage_id == stage.stage_id and result.status == "PASS" for result in self._history):
                continue
            if all(
                artifact_type in self._artifacts and self._artifacts[artifact_type].approved
                for artifact_type in stage.requires_artifact_types
            ):
                return stage
            return None
        return None

    def submit_stage_artifact(self, stage_id: str, artifact: StageArtifact) -> StageResult:
        stage = next((item for item in self.stages if item.stage_id == stage_id), None)
        if stage is None:
            raise KeyError(stage_id)

        expected = self.available_stage()
        if expected is None or expected.stage_id != stage_id:
            raise ValueError(f"stage {stage_id} is not currently executable")

        blockers: list[str] = []
        if artifact.producer_agent_id != stage.agent_id:
            blockers.append("artifact producer does not own this stage")
        if artifact.artifact_type != stage.produces_artifact_type:
            blockers.append(
                f"expected {stage.produces_artifact_type}, got {artifact.artifact_type}"
            )
        if stage.requires_approval and not artifact.approved:
            blockers.append("artifact is not approved")

        if blockers:
            result = StageResult(
                stage_id=stage.stage_id,
                agent_id=stage.agent_id,
                status="BLOCKED",
                artifact=None,
                blocking_findings=tuple(blockers),
            )
            self._history.append(result)
            return result

        self._artifacts[artifact.artifact_type] = artifact
        result = StageResult(
            stage_id=stage.stage_id,
            agent_id=stage.agent_id,
            status="PASS",
            artifact=artifact,
        )
        self._history.append(result)
        return result

    def status(self) -> dict[str, Any]:
        next_stage = self.available_stage()
        return {
            "completed_stages": [
                result.stage_id for result in self._history if result.status == "PASS"
            ],
            "next_stage": next_stage.stage_id if next_stage else None,
            "artifacts": {
                key: {
                    "artifact_id": value.artifact_id,
                    "producer_agent_id": value.producer_agent_id,
                    "approved": value.approved,
                    "artifact_hash": value.artifact_hash,
                }
                for key, value in sorted(self._artifacts.items())
            },
            "history": [
                {
                    "stage_id": result.stage_id,
                    "agent_id": result.agent_id,
                    "status": result.status,
                    "blocking_findings": result.blocking_findings,
                }
                for result in self._history
            ],
        }

    def workflow_hash(self) -> str:
        payload = {
            "stages": [asdict(stage) for stage in self.stages],
            "status": self.status(),
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()
