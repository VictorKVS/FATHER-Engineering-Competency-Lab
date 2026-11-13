from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BlockDescriptor:
    block_id: str
    version: str
    kind: str
    capabilities: frozenset[str]
    requires: frozenset[str] = frozenset()
    reusable: bool = True
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BlockMatchResult:
    required_capabilities: tuple[str, ...]
    selected_blocks: tuple[BlockDescriptor, ...]
    unresolved_capabilities: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.unresolved_capabilities


class BlockCatalog:
    """Deterministic reusable block catalog for product composition."""

    def __init__(self, blocks: Iterable[BlockDescriptor] | None = None) -> None:
        self._blocks: dict[str, BlockDescriptor] = {}
        for block in blocks or ():
            self.register(block)

    def register(self, block: BlockDescriptor) -> None:
        current = self._blocks.get(block.block_id)
        if current and current.version != block.version:
            raise ValueError(
                f"block version conflict for {block.block_id}: "
                f"{current.version} != {block.version}"
            )
        self._blocks[block.block_id] = block

    def list(self) -> list[BlockDescriptor]:
        return sorted(self._blocks.values(), key=lambda b: b.block_id)

    def match(self, required_capabilities: Iterable[str]) -> BlockMatchResult:
        required = set(required_capabilities)
        unresolved = set(required)
        selected: list[BlockDescriptor] = []

        # Greedy but deterministic: maximize uncovered capabilities, then stable block_id.
        candidates = [b for b in self.list() if b.reusable]
        while unresolved:
            scored = []
            for block in candidates:
                coverage = unresolved.intersection(block.capabilities)
                if coverage:
                    scored.append((len(coverage), block.block_id, block))
            if not scored:
                break
            _, _, chosen = sorted(scored, key=lambda x: (-x[0], x[1]))[0]
            selected.append(chosen)
            unresolved.difference_update(chosen.capabilities)
            candidates = [b for b in candidates if b.block_id != chosen.block_id]

        return BlockMatchResult(
            required_capabilities=tuple(sorted(required)),
            selected_blocks=tuple(selected),
            unresolved_capabilities=tuple(sorted(unresolved)),
        )


def build_reference_block_catalog() -> BlockCatalog:
    """Reference catalog mapping existing FATHER capabilities to reusable blocks."""
    return BlockCatalog([
        BlockDescriptor(
            block_id="FTH-RUNTIME-AGENT-001",
            version="1.0",
            kind="runtime",
            capabilities=frozenset({"agent.execute", "workflow.execute"}),
        ),
        BlockDescriptor(
            block_id="FTH-MODEL-ROUTER-001",
            version="1.0",
            kind="model_router",
            capabilities=frozenset({"model.generate"}),
        ),
        BlockDescriptor(
            block_id="FTH-RAG-001",
            version="1.0",
            kind="retrieval",
            capabilities=frozenset({"knowledge.retrieve"}),
        ),
        BlockDescriptor(
            block_id="FTH-AUDIT-EVIDENCE-001",
            version="1.0",
            kind="trust",
            capabilities=frozenset({"audit.write", "evidence.trace", "decision.trace"}),
        ),
        BlockDescriptor(
            block_id="FTH-POLICY-GUARD-001",
            version="1.0",
            kind="security",
            capabilities=frozenset({"policy.enforce"}),
        ),
        BlockDescriptor(
            block_id="FTH-REPORT-001",
            version="1.0",
            kind="output",
            capabilities=frozenset({"report.create"}),
        ),
    ])
