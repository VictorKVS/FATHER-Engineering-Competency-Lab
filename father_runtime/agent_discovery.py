from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import fnmatch
import hashlib
import os
import string


DEFAULT_PATTERNS = (
    "agent.yaml",
    "agent.yml",
    "agent.json",
    "AGENTS.md",
    "*AGENT*.yaml",
    "*AGENT*.yml",
    "*AGENT*.md",
)

DEFAULT_EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "site-packages",
    "$recycle.bin",
    "system volume information",
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
}


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


def available_windows_roots() -> list[str]:
    roots = []
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if os.path.exists(root):
            roots.append(root)
    return roots


def _looks_like_agent_file(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in DEFAULT_PATTERNS)


def _confidence(name: str, text: str) -> tuple[str, list[str]]:
    evidence = [f"filename:{name}"]
    markers = [
        m for m in (
            "agent_id",
            "role",
            "capabilities",
            "prompt",
            "rag_manifest",
            "knowledge_base",
            "tools",
            "permissions",
            "evals",
        )
        if m in text
    ]
    evidence.extend(f"content:{m}" for m in markers)

    canonical_filename = name.lower() in {"agent.yaml", "agent.yml", "agent.json", "agents.md"}
    if canonical_filename and len(markers) >= 4:
        return "CANONICAL", evidence
    if len(markers) >= 3:
        return "HIGH", evidence
    if len(markers) >= 1:
        return "MEDIUM", evidence
    return "LOW", evidence


def discover_local_agents(
    roots: Iterable[str | Path] | None = None,
    *,
    max_files_per_root: int | None = None,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
) -> dict:
    roots = list(roots) if roots is not None else available_windows_roots()
    excluded = {str(x).lower() for x in excluded_dirs}
    results: list[AgentCandidate] = []
    sources = []

    for root_value in roots:
        root = Path(root_value)
        inspected = 0
        truncated = False
        skipped_dirs = 0
        errors = 0

        if not root.exists():
            sources.append({
                "root": str(root),
                "inspected": 0,
                "truncated": False,
                "exists": False,
                "skipped_dirs": 0,
                "errors": 0,
            })
            continue

        try:
            walker = os.walk(root, topdown=True, onerror=lambda _e: None)
            for current, dirs, files in walker:
                kept = []
                for d in dirs:
                    if d.lower() in excluded:
                        skipped_dirs += 1
                    else:
                        kept.append(d)
                dirs[:] = kept

                for filename in files:
                    inspected += 1
                    if max_files_per_root is not None and inspected > max_files_per_root:
                        truncated = True
                        break
                    if not _looks_like_agent_file(filename):
                        continue

                    path = Path(current) / filename
                    try:
                        text = path.read_text(encoding="utf-8", errors="ignore")[:30000]
                    except OSError:
                        errors += 1
                        text = ""

                    confidence, evidence = _confidence(filename, text)
                    if confidence == "LOW" and filename.lower() not in {"agent.yaml","agent.yml","agent.json","agents.md"}:
                        continue

                    results.append(AgentCandidate(
                        discovery_id=_id(str(path)),
                        source="LOCAL_FILESYSTEM",
                        locator=str(path),
                        detected_name=path.parent.name if filename.lower().startswith("agent.") else path.stem,
                        confidence=confidence,
                        evidence=tuple(evidence),
                    ))

                if truncated:
                    break
        except OSError:
            errors += 1

        sources.append({
            "root": str(root),
            "inspected": inspected if not truncated else max_files_per_root,
            "truncated": truncated,
            "exists": True,
            "skipped_dirs": skipped_dirs,
            "errors": errors,
        })

    rank = {"CANONICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    results.sort(key=lambda x: (rank.get(x.confidence, 9), x.detected_name.lower(), x.locator.lower()))

    return {
        "schema": "FATHER_AGENT_DISCOVERY_RESULTS_V2",
        "mode": "READ_ONLY",
        "scope": "ALL_AVAILABLE_WINDOWS_DRIVES" if roots else "EMPTY",
        "candidates": [asdict(x) for x in results],
        "sources": sources,
        "count": len(results),
        "confidence_counts": {
            key: sum(1 for x in results if x.confidence == key)
            for key in ("CANONICAL", "HIGH", "MEDIUM", "LOW")
        },
    }
