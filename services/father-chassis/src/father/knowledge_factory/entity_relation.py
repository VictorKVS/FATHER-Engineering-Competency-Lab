from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from father.knowledge_factory.chunk_normalization import NormalizedChunkSet


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class ExtractionPolicy:
    policy_id: str
    version: str
    entity_types: tuple[str, ...] = ("TERM",)
    relation_types: tuple[str, ...] = ("POINTS_TO",)
    min_confidence: float = 0.8

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("policy version is required")
        if not 0.0 <= self.min_confidence <= 1.0:
            errors.append("min_confidence must be within [0,1]")
        if "TERM" not in self.entity_types:
            errors.append("reference extractor requires TERM entity type")
        if "POINTS_TO" not in self.relation_types:
            errors.append("reference extractor requires POINTS_TO relation type")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class EntityRecord:
    entity_id: str
    entity_type: str
    canonical_name: str
    aliases: tuple[str, ...]
    confidence: float
    evidence_chunk_ids: tuple[str, ...]
    entity_hash: str


@dataclass(frozen=True, slots=True)
class RelationRecord:
    relation_id: str
    relation_type: str
    subject_entity_id: str
    object_entity_id: str
    confidence: float
    evidence_chunk_ids: tuple[str, ...]
    relation_hash: str


@dataclass(frozen=True, slots=True)
class ExtractionSet:
    extraction_set_id: str
    chunk_set_id: str
    chunk_set_hash: str
    extractor_id: str
    extractor_version: str
    policy_id: str
    policy_version: str
    entities: tuple[EntityRecord, ...]
    relations: tuple[RelationRecord, ...]
    extraction_set_hash: str


@dataclass(frozen=True, slots=True)
class ExtractionDecision:
    status: str
    extraction_set: ExtractionSet | None
    diagnostics: tuple[str, ...] = ()


class DeterministicRuleExtractor:
    extractor_id = "FTH-DETERMINISTIC-RULE-EXTRACTOR"
    extractor_version = "1.0.0"

    _entity_pattern = re.compile(r"\b[A-Z][A-Za-z0-9_-]{2,}\b")
    _relation_pattern = re.compile(
        r"\b([A-Z][A-Za-z0-9_-]{2,})\s*->\s*([A-Z][A-Za-z0-9_-]{2,})\b"
    )

    @staticmethod
    def _validate_chunk_set(chunk_set: NormalizedChunkSet) -> tuple[str, ...]:
        errors: list[str] = []
        expected = list(range(len(chunk_set.chunks)))
        actual = [chunk.ordinal for chunk in chunk_set.chunks]
        if actual != expected:
            errors.append("chunk ordinals are not contiguous")
        seen_ids: set[str] = set()
        for chunk in chunk_set.chunks:
            if chunk.chunk_id in seen_ids:
                errors.append(f"duplicate chunk_id: {chunk.chunk_id}")
            seen_ids.add(chunk.chunk_id)
            if chunk.source_id != chunk_set.source_id:
                errors.append(f"chunk {chunk.chunk_id} source_id mismatch")
            if chunk.document_id != chunk_set.document_id:
                errors.append(f"chunk {chunk.chunk_id} document_id mismatch")
            if chunk.document_hash != chunk_set.document_hash:
                errors.append(f"chunk {chunk.chunk_id} document_hash mismatch")
            if not chunk.text.strip():
                errors.append(f"chunk {chunk.chunk_id} is empty")
        return tuple(errors)

    @staticmethod
    def _entity_hash(
        policy: ExtractionPolicy,
        name: str,
        evidence_chunk_ids: tuple[str, ...],
        confidence: float,
    ) -> str:
        payload = {
            "entity_type": "TERM",
            "canonical_name": name,
            "aliases": (),
            "confidence": confidence,
            "evidence_chunk_ids": tuple(sorted(evidence_chunk_ids)),
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()

    @staticmethod
    def _relation_hash(
        policy: ExtractionPolicy,
        subject_id: str,
        object_id: str,
        evidence_chunk_ids: tuple[str, ...],
        confidence: float,
    ) -> str:
        payload = {
            "relation_type": "POINTS_TO",
            "subject_entity_id": subject_id,
            "object_entity_id": object_id,
            "confidence": confidence,
            "evidence_chunk_ids": tuple(sorted(evidence_chunk_ids)),
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()

    def extract(
        self,
        chunk_set: NormalizedChunkSet,
        policy: ExtractionPolicy,
    ) -> ExtractionDecision:
        diagnostics = list(policy.validate())
        diagnostics.extend(self._validate_chunk_set(chunk_set))
        if diagnostics:
            return ExtractionDecision("REJECTED", None, tuple(diagnostics))

        evidence_by_entity: dict[str, set[str]] = {}
        explicit_relations: list[tuple[str, str, str]] = []

        for chunk in chunk_set.chunks:
            for name in self._entity_pattern.findall(chunk.text):
                evidence_by_entity.setdefault(name, set()).add(chunk.chunk_id)
            for subject, obj in self._relation_pattern.findall(chunk.text):
                explicit_relations.append((subject, obj, chunk.chunk_id))
                evidence_by_entity.setdefault(subject, set()).add(chunk.chunk_id)
                evidence_by_entity.setdefault(obj, set()).add(chunk.chunk_id)

        entity_confidence = max(policy.min_confidence, 0.9)
        entities: list[EntityRecord] = []
        entity_id_by_name: dict[str, str] = {}

        for name in sorted(evidence_by_entity):
            evidence_ids = tuple(sorted(evidence_by_entity[name]))
            entity_hash = self._entity_hash(
                policy,
                name,
                evidence_ids,
                entity_confidence,
            )
            entity = EntityRecord(
                entity_id=f"ENT-{entity_hash[:16]}",
                entity_type="TERM",
                canonical_name=name,
                aliases=(),
                confidence=entity_confidence,
                evidence_chunk_ids=evidence_ids,
                entity_hash=entity_hash,
            )
            entities.append(entity)
            entity_id_by_name[name] = entity.entity_id

        relation_confidence = max(policy.min_confidence, 0.95)
        relations: list[RelationRecord] = []
        seen_relation_keys: set[tuple[str, str, str]] = set()
        for subject_name, object_name, chunk_id in explicit_relations:
            subject_id = entity_id_by_name.get(subject_name)
            object_id = entity_id_by_name.get(object_name)
            if subject_id is None or object_id is None:
                continue
            key = ("POINTS_TO", subject_id, object_id)
            if key in seen_relation_keys:
                continue
            seen_relation_keys.add(key)
            evidence_ids = (chunk_id,)
            relation_hash = self._relation_hash(
                policy,
                subject_id,
                object_id,
                evidence_ids,
                relation_confidence,
            )
            relations.append(
                RelationRecord(
                    relation_id=f"REL-{relation_hash[:16]}",
                    relation_type="POINTS_TO",
                    subject_entity_id=subject_id,
                    object_entity_id=object_id,
                    confidence=relation_confidence,
                    evidence_chunk_ids=evidence_ids,
                    relation_hash=relation_hash,
                )
            )

        valid_chunk_ids = {chunk.chunk_id for chunk in chunk_set.chunks}
        entity_ids = {entity.entity_id for entity in entities}
        integrity_errors: list[str] = []
        for entity in entities:
            if not entity.evidence_chunk_ids:
                integrity_errors.append(f"entity {entity.entity_id} missing evidence")
            if not set(entity.evidence_chunk_ids) <= valid_chunk_ids:
                integrity_errors.append(f"entity {entity.entity_id} references unknown chunk")
        for relation in relations:
            if relation.subject_entity_id not in entity_ids:
                integrity_errors.append(f"relation {relation.relation_id} dangling subject")
            if relation.object_entity_id not in entity_ids:
                integrity_errors.append(f"relation {relation.relation_id} dangling object")
            if not relation.evidence_chunk_ids:
                integrity_errors.append(f"relation {relation.relation_id} missing evidence")
            if not set(relation.evidence_chunk_ids) <= valid_chunk_ids:
                integrity_errors.append(f"relation {relation.relation_id} references unknown chunk")
        if integrity_errors:
            return ExtractionDecision("REJECTED", None, tuple(integrity_errors))

        set_payload = {
            "chunk_set_id": chunk_set.chunk_set_id,
            "chunk_set_hash": chunk_set.chunk_set_hash,
            "extractor_id": self.extractor_id,
            "extractor_version": self.extractor_version,
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "entity_hashes": [entity.entity_hash for entity in entities],
            "relation_hashes": [relation.relation_hash for relation in relations],
        }
        set_hash = sha256(_canonical(set_payload).encode("utf-8")).hexdigest()
        extraction_set = ExtractionSet(
            extraction_set_id=f"EXSET-{set_hash[:16]}",
            chunk_set_id=chunk_set.chunk_set_id,
            chunk_set_hash=chunk_set.chunk_set_hash,
            extractor_id=self.extractor_id,
            extractor_version=self.extractor_version,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            entities=tuple(entities),
            relations=tuple(relations),
            extraction_set_hash=set_hash,
        )
        return ExtractionDecision("EXTRACTED", extraction_set)
