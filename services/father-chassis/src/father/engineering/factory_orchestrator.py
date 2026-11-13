from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from father.engineering.competency_admission import (
    CompetencyAdmissionGate,
    CompetencyAdmissionRequest,
)
from father.engineering.factory_agents import FactoryAgentCatalog, build_factory_agent_catalog
from father.engineering.stage_artifacts import (
    StagePayload,
    deserialize_stage_payload,
    serialize_stage_payload,
)


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class StageArtifact:
    artifact_id: str
    artifact_type: str
    producer_agent_id: str
    payload: StagePayload
    approved: bool
    payload_schema_version: int = 1
    evidence_refs: tuple[str, ...] = ()
    artifact_hash: str = ""

    def __post_init__(self) -> None:
        if not self.artifact_id.strip():
            raise ValueError("artifact_id is required")
        if not self.artifact_type.strip():
            raise ValueError("artifact_type is required")
        if not self.producer_agent_id.strip():
            raise ValueError("producer_agent_id is required")
        payload_data = serialize_stage_payload(
            self.artifact_type,
            self.payload_schema_version,
            self.payload,
        )
        if not self.artifact_hash:
            payload = {
                "artifact_id": self.artifact_id,
                "artifact_type": self.artifact_type,
                "payload_schema_version": self.payload_schema_version,
                "producer_agent_id": self.producer_agent_id,
                "payload_data": payload_data,
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
    competency_qualification_id: str | None = None
    competency_evidence_ids: tuple[str, ...] = ()


class FactoryEngineeringWorkflow:
    """Fail-closed role orchestration for engineering delivery."""

    NAMESPACE = "factory_engineering_workflow"
    SNAPSHOT_SCHEMA_VERSION = 3

    def __init__(
        self,
        catalog: FactoryAgentCatalog | None = None,
        *,
        store=None,
        workflow_id: str = "default",
        competency_gate: CompetencyAdmissionGate | None = None,
        require_competency_admission: bool = False,
    ) -> None:
        if not workflow_id.strip():
            raise ValueError("workflow_id is required")
        self.catalog = catalog or build_factory_agent_catalog()
        self.store = store
        self.workflow_id = workflow_id
        self.competency_gate = competency_gate
        self.require_competency_admission = require_competency_admission
        if self.require_competency_admission and self.competency_gate is None:
            raise ValueError("competency admission is required but no competency_gate is configured")
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
        self._restore()

    @staticmethod
    def _artifact_to_dict(artifact: StageArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.artifact_id,
            "artifact_type": artifact.artifact_type,
            "producer_agent_id": artifact.producer_agent_id,
            "payload_schema_version": artifact.payload_schema_version,
            "payload_data": serialize_stage_payload(
                artifact.artifact_type,
                artifact.payload_schema_version,
                artifact.payload,
            ),
            "approved": artifact.approved,
            "evidence_refs": list(artifact.evidence_refs),
            "artifact_hash": artifact.artifact_hash,
        }

    @staticmethod
    def _artifact_from_dict(raw: dict[str, Any]) -> StageArtifact:
        stored_hash = str(raw["artifact_hash"])
        artifact_type = str(raw["artifact_type"])
        schema_version = int(raw["payload_schema_version"])
        payload_data = raw["payload_data"]
        if not isinstance(payload_data, dict):
            raise ValueError("malformed stage artifact payload_data")
        candidate = StageArtifact(
            artifact_id=str(raw["artifact_id"]),
            artifact_type=artifact_type,
            producer_agent_id=str(raw["producer_agent_id"]),
            payload=deserialize_stage_payload(
                artifact_type,
                schema_version,
                dict(payload_data),
            ),
            approved=bool(raw["approved"]),
            payload_schema_version=schema_version,
            evidence_refs=tuple(str(x) for x in raw.get("evidence_refs", ())),
        )
        if candidate.artifact_hash != stored_hash:
            raise ValueError(
                f"stage artifact hash mismatch for {candidate.artifact_id}: "
                f"{stored_hash} != {candidate.artifact_hash}"
            )
        return candidate

    def _snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": self.SNAPSHOT_SCHEMA_VERSION,
            "workflow_id": self.workflow_id,
            "artifacts": {
                key: self._artifact_to_dict(value)
                for key, value in sorted(self._artifacts.items())
            },
            "history": [
                {
                    "stage_id": result.stage_id,
                    "agent_id": result.agent_id,
                    "status": result.status,
                    "artifact_type": (
                        result.artifact.artifact_type if result.artifact is not None else None
                    ),
                    "blocking_findings": list(result.blocking_findings),
                    "competency_qualification_id": result.competency_qualification_id,
                    "competency_evidence_ids": list(result.competency_evidence_ids),
                }
                for result in self._history
            ],
        }

    def _persist(self) -> None:
        if self.store is not None:
            self.store.set(self.NAMESPACE, self.workflow_id, self._snapshot())

    def _restore(self) -> None:
        if self.store is None:
            return
        raw = self.store.get(self.NAMESPACE, self.workflow_id)
        if raw is None:
            return
        if int(raw.get("schema_version", -1)) != self.SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("unsupported factory engineering workflow snapshot schema")
        if str(raw.get("workflow_id", "")) != self.workflow_id:
            raise ValueError("workflow_id mismatch in persisted workflow snapshot")

        artifacts_raw = raw.get("artifacts")
        history_raw = raw.get("history")
        if not isinstance(artifacts_raw, dict) or not isinstance(history_raw, list):
            raise ValueError("malformed factory engineering workflow snapshot")

        self._artifacts = {
            str(key): self._artifact_from_dict(dict(value))
            for key, value in artifacts_raw.items()
        }

        restored_history: list[StageResult] = []
        for item in history_raw:
            stage_id = str(item["stage_id"])
            agent_id = str(item["agent_id"])
            status = str(item["status"])
            artifact_type = item.get("artifact_type")
            artifact = (
                self._artifacts.get(str(artifact_type))
                if artifact_type is not None
                else None
            )
            restored_history.append(
                StageResult(
                    stage_id=stage_id,
                    agent_id=agent_id,
                    status=status,
                    artifact=artifact,
                    blocking_findings=tuple(
                        str(x) for x in item.get("blocking_findings", ())
                    ),
                    competency_qualification_id=(
                        None
                        if item.get("competency_qualification_id") is None
                        else str(item["competency_qualification_id"])
                    ),
                    competency_evidence_ids=tuple(
                        str(x) for x in item.get("competency_evidence_ids", ())
                    ),
                )
            )
        self._history = restored_history

    def add_external_artifact(self, artifact: StageArtifact) -> None:
        if not artifact.approved:
            raise ValueError("external artifact must be approved")
        self._artifacts[artifact.artifact_type] = artifact
        self._persist()

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

        competency_qualification_id: str | None = None
        competency_evidence_ids: tuple[str, ...] = ()
        if self.require_competency_admission:
            assert self.competency_gate is not None
            decision = self.competency_gate.evaluate(
                CompetencyAdmissionRequest(
                    workflow_id=self.workflow_id,
                    stage_id=stage.stage_id,
                    agent_id=stage.agent_id,
                )
            )
            competency_qualification_id = decision.trust_qualification_id
            competency_evidence_ids = decision.evidence_ids
            if not decision.admitted:
                blockers.extend(
                    f"competency admission: {reason}" for reason in decision.reasons
                )

        if blockers:
            result = StageResult(
                stage_id=stage.stage_id,
                agent_id=stage.agent_id,
                status="BLOCKED",
                artifact=None,
                blocking_findings=tuple(blockers),
                competency_qualification_id=competency_qualification_id,
                competency_evidence_ids=competency_evidence_ids,
            )
            self._history.append(result)
            self._persist()
            return result

        self._artifacts[artifact.artifact_type] = artifact
        result = StageResult(
            stage_id=stage.stage_id,
            agent_id=stage.agent_id,
            status="PASS",
            artifact=artifact,
            competency_qualification_id=competency_qualification_id,
            competency_evidence_ids=competency_evidence_ids,
        )
        self._history.append(result)
        self._persist()
        return result

    def status(self) -> dict[str, Any]:
        next_stage = self.available_stage()
        return {
            "workflow_id": self.workflow_id,
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
                    "competency_qualification_id": result.competency_qualification_id,
                    "competency_evidence_ids": result.competency_evidence_ids,
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
