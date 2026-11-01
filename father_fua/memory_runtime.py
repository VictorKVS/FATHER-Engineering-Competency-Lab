from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryItem:
    content: str
    scope: str
    provenance: str
    confidence: float
    trusted: bool=False


class MemoryStore:
    def __init__(self) -> None:
        self.items:list[MemoryItem]=[]

    def write(self,item:MemoryItem,*,approved:bool=False) -> str:
        if not item.provenance:
            return "QUARANTINE"
        if item.confidence < 0.5:
            return "QUARANTINE"
        if item.trusted and not approved:
            return "REQUIRE_APPROVAL"
        self.items.append(item)
        return "ALLOW"

    def query(self,scope:str,query:str) -> list[MemoryItem]:
        return [x for x in self.items if x.scope==scope and query.lower() in x.content.lower()]
