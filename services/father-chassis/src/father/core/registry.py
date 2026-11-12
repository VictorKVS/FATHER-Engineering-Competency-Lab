from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BlockDescriptor:
    block_id: str
    version: str
    kind: str
    instance: Any
    capabilities: frozenset[str] = field(default_factory=frozenset)
    compatibility: str = "father-chassis>=0.3,<1.0"


class BlockRegistry:
    def __init__(self) -> None:
        self._blocks: dict[str, BlockDescriptor] = {}

    def register(self, block: BlockDescriptor) -> None:
        if block.block_id in self._blocks:
            raise ValueError(f"duplicate block_id: {block.block_id}")
        self._blocks[block.block_id] = block

    def get(self, block_id: str) -> BlockDescriptor:
        try:
            return self._blocks[block_id]
        except KeyError as exc:
            raise KeyError(f"unknown block_id: {block_id}") from exc

    def list(self) -> list[BlockDescriptor]:
        return list(self._blocks.values())

    def health(self) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for block_id, desc in self._blocks.items():
            checker = getattr(desc.instance, "health", None)
            result[block_id] = bool(checker()) if callable(checker) else True
        return result
