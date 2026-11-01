from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class KnowledgeItem:
    knowledge_id: str
    term: str
    definition: str
    definition_type: str
    provenance: tuple[str, ...]
    confidence: float
    review_status: str
    canonical: bool = False
    revoked_support: bool = False


class KnowledgeRegistry:
    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}

    def register_candidate(
        self,
        *,
        knowledge_id: str,
        term: str,
        definition: str,
        definition_type: str,
        provenance: list[str],
        confidence: float,
    ) -> KnowledgeItem:
        if not provenance:
            raise ValueError("provenance required")
        if definition_type not in {"EXPLICIT_SOURCE", "DISTRIBUTED_SOURCE", "ALINA_SYNTHESIS"}:
            raise ValueError("invalid definition_type")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence out of range")
        item = KnowledgeItem(
            knowledge_id=knowledge_id,
            term=term,
            definition=definition,
            definition_type=definition_type,
            provenance=tuple(provenance),
            confidence=confidence,
            review_status="CANDIDATE",
        )
        self._items[knowledge_id] = item
        return item

    def canonicalize(self, knowledge_id: str, *, approved: bool) -> KnowledgeItem:
        item = self._items[knowledge_id]
        if not approved:
            raise PermissionError("validation gate not approved")
        if item.revoked_support:
            raise ValueError("support revoked")
        updated = replace(item, review_status="VALIDATED", canonical=True)
        self._items[knowledge_id] = updated
        return updated

    def revoke_support(self, knowledge_id: str) -> KnowledgeItem:
        item = self._items[knowledge_id]
        updated = replace(item, revoked_support=True, canonical=False, review_status="REVIEW_REQUIRED")
        self._items[knowledge_id] = updated
        return updated

    def by_term(self, term: str) -> list[KnowledgeItem]:
        return [x for x in self._items.values() if x.term.lower() == term.lower()]
