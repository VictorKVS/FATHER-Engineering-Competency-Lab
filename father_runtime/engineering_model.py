from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CRITICAL_TYPES = {"REQUIREMENT", "SECURITY_REQUIREMENT", "SKILL", "KNOWLEDGE_NODE", "RELEASE"}


@dataclass
class ValidationIssue:
    code: str
    entity_id: str
    message: str
    severity: str = "ERROR"


@dataclass
class ValidationResult:
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)


class EngineeringModelValidator:
    def validate(self, project: dict[str, Any]) -> ValidationResult:
        issues: list[ValidationIssue] = []
        entities = {e["id"]: e for e in project.get("entities", [])}
        edges = project.get("edges", [])

        outgoing: dict[str, list[dict[str, Any]]] = {}
        incoming: dict[str, list[dict[str, Any]]] = {}
        for edge in edges:
            outgoing.setdefault(edge["from"], []).append(edge)
            incoming.setdefault(edge["to"], []).append(edge)

        for entity_id, entity in entities.items():
            etype = entity.get("type")
            if not entity.get("version"):
                issues.append(ValidationIssue("MISSING_VERSION", entity_id, "Entity has no version"))
            if not entity.get("owner"):
                issues.append(ValidationIssue("MISSING_OWNER", entity_id, "Entity has no owner"))

            if etype == "REQUIREMENT" and not self._has_path(entity_id, entities, outgoing, {"EVAL_CASE", "EVIDENCE"}):
                issues.append(ValidationIssue("REQ_NO_EVIDENCE_PATH", entity_id, "Requirement has no trace to eval/evidence"))

            if etype == "KNOWLEDGE_NODE":
                has_source = any(
                    entities.get(e["to"], {}).get("type") == "SOURCE"
                    for e in outgoing.get(entity_id, [])
                ) or any(
                    entities.get(e["from"], {}).get("type") == "SOURCE"
                    for e in incoming.get(entity_id, [])
                )
                if not has_source:
                    issues.append(ValidationIssue("KNOWLEDGE_NO_SOURCE", entity_id, "Knowledge node has no source provenance"))

            if etype == "SKILL" and not self._has_path(entity_id, entities, outgoing, {"EVAL_CASE"}):
                issues.append(ValidationIssue("SKILL_NO_EVAL", entity_id, "Skill has no evaluation path"))

            if etype == "RELEASE":
                has_evidence = any(
                    entities.get(e["from"], {}).get("type") == "EVIDENCE"
                    for e in incoming.get(entity_id, [])
                )
                if not has_evidence:
                    issues.append(ValidationIssue("RELEASE_NO_EVIDENCE", entity_id, "Release has no supporting evidence"))

        return ValidationResult(valid=not issues, issues=issues)

    def _has_path(
        self,
        start: str,
        entities: dict[str, dict[str, Any]],
        outgoing: dict[str, list[dict[str, Any]]],
        target_types: set[str],
    ) -> bool:
        seen = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for edge in outgoing.get(current, []):
                nxt = edge["to"]
                if nxt in seen:
                    continue
                if entities.get(nxt, {}).get("type") in target_types:
                    return True
                seen.add(nxt)
                stack.append(nxt)
        return False
