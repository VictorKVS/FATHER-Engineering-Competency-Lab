from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import fnmatch
import hashlib
import json


DEFAULT_PATTERNS = (
    "agent.yaml",
    "agent.yml",
    "agent.json",
    "AGENTS.md",
    "*AGENT*.yaml",
    "*AGENT*.yml",
    "*AGENT*.md",
)


@dataclass(frozen=True)
class AgentCandidate:
    discovery_id: str
    source: str
    locator: str
    detected_name: str
    confidence: str
    evidence: tuple[str, ...]


def _id(locator: str) -> str:
    return "DISC-" + hashlib.sha256(locator.encode("utf-8")).hexdigest()[:12].upper()


def discover_local_agents(
    roots: Iterable[str | Path],
    *,
    max_files_per_root: int = 20000,
) -> dict:
    results: list[AgentCandidate] = []
    sources = []

    for root_value in roots:
        root = Path(root_value)
        inspected = 0
        truncated = False
        if not root.exists():
            sources.append({"root": str(root), "inspected": 0, "truncated": False, "exists": False})
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            inspected += 1
            if inspected > max_files_per_root:
                truncated = True
                break

            name = path.name
            if not any(fnmatch.fnmatch(name, pattern) for pattern in DEFAULT_PATTERNS):
                continue

            evidence = [f"filename:{name}"]
            confidence = "MEDIUM"
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
                markers = [m for m in ("agent_id","role","capabilities","prompt","rag_manifest","knowledge_base") if m in text]
                evidence.extend(f"content:{m}" for m in markers)
                if len(markers) >= 3:
                    confidence = "HIGH"
            except OSError:
                pass

            results.append(AgentCandidate(
                discovery_id=_id(str(path.resolve())),
                source="LOCAL_FILESYSTEM",
                locator=str(path),
                detected_name=path.parent.name if name.lower().startswith("agent.") else path.stem,
                confidence=confidence,
                evidence=tuple(evidence),
            ))

        sources.append({"root": str(root), "inspected": min(inspected,max_files_per_root), "truncated": truncated, "exists": True})

    return {
        "schema": "FATHER_AGENT_DISCOVERY_RESULTS_V1",
        "mode": "READ_ONLY",
        "candidates": [asdict(x) for x in results],
        "sources": sources,
        "count": len(results),
    }
