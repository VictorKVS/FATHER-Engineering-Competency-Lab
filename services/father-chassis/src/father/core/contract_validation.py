from __future__ import annotations
from .registry import BlockDescriptor

REQUIRED_BY_KIND = {
    "model": frozenset({"generate"}), "rag": frozenset({"retrieve"}),
    "tool": frozenset({"create_report"}), "guardrail": frozenset({"authorize"}),
    "state": frozenset({"get","set"}),
}

def validate_block(block: BlockDescriptor) -> list[str]:
    errors: list[str] = []
    if not block.block_id.startswith("FTH-"): errors.append("block_id must start with FTH-")
    if not block.version: errors.append("version is required")
    required = REQUIRED_BY_KIND.get(block.kind, frozenset())
    missing = required - block.capabilities
    if missing: errors.append("missing capabilities: " + ",".join(sorted(missing)))
    return errors
