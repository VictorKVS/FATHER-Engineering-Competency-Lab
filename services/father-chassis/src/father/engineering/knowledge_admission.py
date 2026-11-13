from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from father.engineering.factory_agents import FactoryAgentCatalog


@dataclass(frozen=True, slots=True)
class KnowledgeBaseRelease:
    release_id: str
    kb_id: str
    version: str
    release_hash: str
    status: str
    source_set_hashes: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    retrieval_evidence_refs: tuple[str, ...]
    retrieval_metrics: dict[str, float] = field(default_factory=dict)
    created_at: str = ""

    def validation_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.release_id.strip():
            errors.append("release_id is required")
        if not self.kb_id.strip():
            errors.append("kb_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if len(self.release_hash) != 64:
            errors.append("release_hash must be a SHA-256 hex digest")
        else:
            try:
                int(self.release_hash, 16)
            except ValueError:
                errors.append("release_hash must be a SHA-256 hex digest")
        if self.status != "QUALIFIED":
            errors.append(f"release status is not QUALIFIED: {self.status}")
        if not self.source_set_hashes:
            errors.append("source_set_hashes are required")
        if not self.provenance_refs:
            errors.append("provenance_refs are required")
        if not self.retrieval_evidence_refs:
            errors.append("retrieval_evidence_refs are required")
        if not self.retrieval_metrics:
            errors.append("retrieval_metrics are required")
        return tuple(errors)


class KnowledgeReleaseRegistry(Protocol):
    def get_for_kb(self, kb_id: str) -> KnowledgeBaseRelease | None: ...


class InMemoryKnowledgeReleaseRegistry:
    def __init__(self, releases: tuple[KnowledgeBaseRelease, ...] = ()) -> None:
        self._releases: dict[str, KnowledgeBaseRelease] = {}
        for release in releases:
            if release.kb_id in self._releases:
                raise ValueError(f"duplicate active knowledge release for {release.kb_id}")
            self._releases[release.kb_id] = release

    def get_for_kb(self, kb_id: str) -> KnowledgeBaseRelease | None:
        return self._releases.get(kb_id)


@dataclass(frozen=True, slots=True)
class KnowledgeAdmissionRequest:
    workflow_id: str
    stage_id: str
    agent_id: str


@dataclass(frozen=True, slots=True)
class KnowledgeAdmissionDecision:
    workflow_id: str
    stage_id: str
    agent_id: str
    admitted: bool
    release_ids: tuple[str, ...]
    release_hashes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    reasons: tuple[str, ...]


class QualifiedKnowledgeAdmissionGate:
    def __init__(
        self,
        *,
        catalog: FactoryAgentCatalog,
        registry: KnowledgeReleaseRegistry,
    ) -> None:
        self.catalog = catalog
        self.registry = registry

    def evaluate(self, request: KnowledgeAdmissionRequest) -> KnowledgeAdmissionDecision:
        try:
            agent = self.catalog.by_id(request.agent_id)
        except KeyError:
            return KnowledgeAdmissionDecision(
                request.workflow_id,
                request.stage_id,
                request.agent_id,
                False,
                (),
                (),
                (),
                (f"unknown agent: {request.agent_id}",),
            )

        release_ids: list[str] = []
        release_hashes: list[str] = []
        evidence_refs: list[str] = []
        reasons: list[str] = []

        for kb in agent.knowledge_bases:
            release = self.registry.get_for_kb(kb.kb_id)
            if release is None:
                reasons.append(f"missing qualified knowledge release for {kb.kb_id}")
                continue
            if release.kb_id != kb.kb_id:
                reasons.append(
                    f"knowledge release kb_id mismatch: expected {kb.kb_id}, got {release.kb_id}"
                )
                continue
            release_errors = release.validation_errors()
            if release_errors:
                reasons.extend(f"{kb.kb_id}: {error}" for error in release_errors)
                continue
            release_ids.append(release.release_id)
            release_hashes.append(release.release_hash)
            evidence_refs.extend(release.provenance_refs)
            evidence_refs.extend(release.retrieval_evidence_refs)

        return KnowledgeAdmissionDecision(
            workflow_id=request.workflow_id,
            stage_id=request.stage_id,
            agent_id=request.agent_id,
            admitted=not reasons,
            release_ids=tuple(release_ids),
            release_hashes=tuple(release_hashes),
            evidence_refs=tuple(dict.fromkeys(evidence_refs)),
            reasons=tuple(reasons),
        )
