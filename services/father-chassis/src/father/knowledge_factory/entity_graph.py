from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from father.knowledge_factory.entity_relation import ExtractionSet


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _norm_name(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


@dataclass(frozen=True, slots=True)
class GraphResolutionPolicy:
    policy_id: str
    version: str
    exact_name_same_type_merge: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("policy version is required")
        if not self.exact_name_same_type_merge:
            errors.append("reference v1 requires exact_name_same_type_merge=true")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class GraphNode:
    node_id: str
    entity_type: str
    canonical_name: str
    source_entity_ids: tuple[str, ...]
    evidence_chunk_ids: tuple[str, ...]
    node_hash: str


@dataclass(frozen=True, slots=True)
class GraphEdge:
    edge_id: str
    relation_type: str
    subject_node_id: str
    object_node_id: str
    source_relation_ids: tuple[str, ...]
    evidence_chunk_ids: tuple[str, ...]
    edge_hash: str


@dataclass(frozen=True, slots=True)
class ResolutionConflict:
    conflict_type: str
    normalized_name: str
    entity_types: tuple[str, ...]
    source_entity_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class KnowledgeGraphSnapshot:
    graph_id: str
    policy_id: str
    policy_version: str
    source_extraction_set_ids: tuple[str, ...]
    source_extraction_set_hashes: tuple[str, ...]
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    conflicts: tuple[ResolutionConflict, ...]
    graph_hash: str


@dataclass(frozen=True, slots=True)
class GraphBuildDecision:
    status: str
    graph: KnowledgeGraphSnapshot | None
    diagnostics: tuple[str, ...] = ()


class DeterministicEntityGraphBuilder:
    @staticmethod
    def _validate_sets(extraction_sets: tuple[ExtractionSet, ...]) -> tuple[str, ...]:
        errors: list[str] = []
        ids: set[str] = set()
        hashes: set[str] = set()
        for extraction_set in extraction_sets:
            if extraction_set.extraction_set_id in ids:
                errors.append(f"duplicate extraction_set_id: {extraction_set.extraction_set_id}")
            if extraction_set.extraction_set_hash in hashes:
                errors.append(f"duplicate extraction_set_hash: {extraction_set.extraction_set_hash}")
            ids.add(extraction_set.extraction_set_id)
            hashes.add(extraction_set.extraction_set_hash)

            entity_ids = {entity.entity_id for entity in extraction_set.entities}
            for relation in extraction_set.relations:
                if relation.subject_entity_id not in entity_ids:
                    errors.append(f"dangling relation subject: {relation.relation_id}")
                if relation.object_entity_id not in entity_ids:
                    errors.append(f"dangling relation object: {relation.relation_id}")
        return tuple(errors)

    @staticmethod
    def _node_hash(
        policy: GraphResolutionPolicy,
        entity_type: str,
        canonical_name: str,
        source_entity_ids: tuple[str, ...],
        evidence_chunk_ids: tuple[str, ...],
    ) -> str:
        payload = {
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "entity_type": entity_type,
            "canonical_name": canonical_name,
            "source_entity_ids": source_entity_ids,
            "evidence_chunk_ids": evidence_chunk_ids,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()

    @staticmethod
    def _edge_hash(
        policy: GraphResolutionPolicy,
        relation_type: str,
        subject_node_id: str,
        object_node_id: str,
        source_relation_ids: tuple[str, ...],
        evidence_chunk_ids: tuple[str, ...],
    ) -> str:
        payload = {
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "relation_type": relation_type,
            "subject_node_id": subject_node_id,
            "object_node_id": object_node_id,
            "source_relation_ids": source_relation_ids,
            "evidence_chunk_ids": evidence_chunk_ids,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()

    def build(
        self,
        extraction_sets: tuple[ExtractionSet, ...],
        policy: GraphResolutionPolicy,
    ) -> GraphBuildDecision:
        diagnostics = list(policy.validate())
        diagnostics.extend(self._validate_sets(extraction_sets))
        if diagnostics:
            return GraphBuildDecision("REJECTED", None, tuple(diagnostics))

        sorted_sets = tuple(
            sorted(extraction_sets, key=lambda item: (item.extraction_set_hash, item.extraction_set_id))
        )

        buckets: dict[tuple[str, str], list] = {}
        types_by_name: dict[str, set[str]] = {}
        source_to_key: dict[str, tuple[str, str]] = {}

        for extraction_set in sorted_sets:
            for entity in sorted(extraction_set.entities, key=lambda item: item.entity_id):
                key = (entity.entity_type, _norm_name(entity.canonical_name))
                buckets.setdefault(key, []).append(entity)
                types_by_name.setdefault(key[1], set()).add(entity.entity_type)
                source_to_key[entity.entity_id] = key

        conflicts: list[ResolutionConflict] = []
        for normalized_name in sorted(types_by_name):
            entity_types = tuple(sorted(types_by_name[normalized_name]))
            if len(entity_types) <= 1:
                continue
            source_ids = sorted(
                entity.entity_id
                for key, entities in buckets.items()
                if key[1] == normalized_name
                for entity in entities
            )
            conflicts.append(
                ResolutionConflict(
                    conflict_type="SAME_NAME_DIFFERENT_TYPE",
                    normalized_name=normalized_name,
                    entity_types=entity_types,
                    source_entity_ids=tuple(source_ids),
                )
            )

        nodes: list[GraphNode] = []
        key_to_node_id: dict[tuple[str, str], str] = {}
        for key in sorted(buckets):
            entities = buckets[key]
            source_entity_ids = tuple(sorted({entity.entity_id for entity in entities}))
            evidence_chunk_ids = tuple(
                sorted({chunk_id for entity in entities for chunk_id in entity.evidence_chunk_ids})
            )
            canonical_name = sorted(
                {entity.canonical_name.strip() for entity in entities},
                key=lambda value: (value.casefold(), value),
            )[0]
            node_hash = self._node_hash(
                policy,
                key[0],
                canonical_name,
                source_entity_ids,
                evidence_chunk_ids,
            )
            node = GraphNode(
                node_id=f"NODE-{node_hash[:16]}",
                entity_type=key[0],
                canonical_name=canonical_name,
                source_entity_ids=source_entity_ids,
                evidence_chunk_ids=evidence_chunk_ids,
                node_hash=node_hash,
            )
            nodes.append(node)
            key_to_node_id[key] = node.node_id

        source_entity_to_node: dict[str, str] = {}
        for source_entity_id, key in source_to_key.items():
            source_entity_to_node[source_entity_id] = key_to_node_id[key]

        edge_buckets: dict[tuple[str, str, str], dict[str, set[str]]] = {}
        for extraction_set in sorted_sets:
            for relation in sorted(extraction_set.relations, key=lambda item: item.relation_id):
                subject_node = source_entity_to_node.get(relation.subject_entity_id)
                object_node = source_entity_to_node.get(relation.object_entity_id)
                if subject_node is None or object_node is None:
                    return GraphBuildDecision(
                        "REJECTED",
                        None,
                        (f"dangling relation endpoint: {relation.relation_id}",),
                    )
                key = (relation.relation_type, subject_node, object_node)
                bucket = edge_buckets.setdefault(
                    key,
                    {"relations": set(), "evidence": set()},
                )
                bucket["relations"].add(relation.relation_id)
                bucket["evidence"].update(relation.evidence_chunk_ids)

        edges: list[GraphEdge] = []
        for key in sorted(edge_buckets):
            bucket = edge_buckets[key]
            source_relation_ids = tuple(sorted(bucket["relations"]))
            evidence_chunk_ids = tuple(sorted(bucket["evidence"]))
            edge_hash = self._edge_hash(
                policy,
                key[0],
                key[1],
                key[2],
                source_relation_ids,
                evidence_chunk_ids,
            )
            edges.append(
                GraphEdge(
                    edge_id=f"EDGE-{edge_hash[:16]}",
                    relation_type=key[0],
                    subject_node_id=key[1],
                    object_node_id=key[2],
                    source_relation_ids=source_relation_ids,
                    evidence_chunk_ids=evidence_chunk_ids,
                    edge_hash=edge_hash,
                )
            )

        node_hashes = [node.node_hash for node in sorted(nodes, key=lambda item: item.node_hash)]
        edge_hashes = [edge.edge_hash for edge in sorted(edges, key=lambda item: item.edge_hash)]
        conflict_payloads = [
            {
                "conflict_type": conflict.conflict_type,
                "normalized_name": conflict.normalized_name,
                "entity_types": conflict.entity_types,
                "source_entity_ids": conflict.source_entity_ids,
            }
            for conflict in sorted(
                conflicts,
                key=lambda item: (item.normalized_name, item.entity_types, item.source_entity_ids),
            )
        ]
        graph_payload = {
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "source_extraction_set_ids": tuple(sorted(item.extraction_set_id for item in sorted_sets)),
            "source_extraction_set_hashes": tuple(sorted(item.extraction_set_hash for item in sorted_sets)),
            "node_hashes": node_hashes,
            "edge_hashes": edge_hashes,
            "conflicts": conflict_payloads,
        }
        graph_hash = sha256(_canonical(graph_payload).encode("utf-8")).hexdigest()
        graph = KnowledgeGraphSnapshot(
            graph_id=f"GRAPH-{graph_hash[:16]}",
            policy_id=policy.policy_id,
            policy_version=policy.version,
            source_extraction_set_ids=tuple(sorted(item.extraction_set_id for item in sorted_sets)),
            source_extraction_set_hashes=tuple(sorted(item.extraction_set_hash for item in sorted_sets)),
            nodes=tuple(sorted(nodes, key=lambda item: item.node_id)),
            edges=tuple(sorted(edges, key=lambda item: item.edge_id)),
            conflicts=tuple(
                sorted(
                    conflicts,
                    key=lambda item: (item.normalized_name, item.entity_types, item.source_entity_ids),
                )
            ),
            graph_hash=graph_hash,
        )
        return GraphBuildDecision("BUILT", graph)
