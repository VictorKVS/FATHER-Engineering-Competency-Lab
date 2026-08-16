"""Seal, preflight and compare isolated FATHER experiment packets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from typing import Any

FIXED_TIMESTAMP = (2026, 8, 16, 0, 0, 0)
CORE_FILES = {"TASK.md", "result-template.json"}
TREATMENT_FILES = {"PAT-GAME-0001.md", "ANTI-GAME-0001.md"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_text(path: Path) -> bytes:
    """Return repository text in the manifest's UTF-8/LF representation."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return (text.rstrip("\n") + "\n").encode()


def verify_packet(packet_dir: Path) -> dict[str, Any]:
    manifest = json.loads((packet_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    actual: dict[str, str] = {}
    combined = bytearray()
    for name, expected in sorted(manifest["allowed_files"].items()):
        data = canonical_text(packet_dir / name)
        actual[name] = digest(data)
        if actual[name] != expected:
            raise ValueError(f"hash mismatch: {name}")
        combined.extend(data)
    context_hash = digest(bytes(combined))
    if context_hash != manifest["allowed_context_sha256"]:
        raise ValueError("allowed context hash mismatch")
    return {"decision": "packet_valid", "files": actual, "allowed_context_sha256": context_hash}


def preflight_inventory(packet_dir: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    verified = verify_packet(packet_dir)
    manifest = json.loads((packet_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    serialized = json.dumps(inventory, sort_keys=True).lower()
    hits = [marker for marker in manifest["blocked_markers"] if marker.lower() in serialized]
    allowed_resources = set(manifest["allowed_files"])
    observed_resources = set(inventory.get("resources", []))
    extra_resources = sorted(observed_resources - allowed_resources)
    controls_ok = (
        inventory.get("network_enabled") is False
        and bool(inventory.get("context_instance_id"))
        and inventory.get("operator_attestation") is True
    )
    clean = not hits and not extra_resources and controls_ok
    return {
        "decision": "preflight_pass" if clean else "preflight_fail",
        "blocked_marker_hits": hits,
        "extra_resources": extra_resources,
        "controls_ok": controls_ok,
        "inventory_sha256": digest(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()),
        "allowed_context_sha256": verified["allowed_context_sha256"],
    }


def build_packet(packet_dir: Path, output: Path) -> dict[str, Any]:
    verified = verify_packet(packet_dir)
    entries = [("MANIFEST.json", canonical_text(packet_dir / "MANIFEST.json"))] + [
        (name, canonical_text(packet_dir / name)) for name in sorted(verified["files"])
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return {"decision": "packet_built", "file": output.name, "sha256": digest(output.read_bytes())}


def _result_without_arm_metadata(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    for field in ("experiment_id", "arm", "learning_claim"):
        result.pop(field)
    return result


def compare_arms(baseline_dir: Path, treatment_dir: Path) -> dict[str, Any]:
    a_verified, b_verified = verify_packet(baseline_dir), verify_packet(treatment_dir)
    a_manifest = json.loads((baseline_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    b_manifest = json.loads((treatment_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    if a_manifest.get("arm") != "baseline" or b_manifest.get("arm") != "treatment":
        raise ValueError("expected baseline A and treatment B arms")
    if set(a_verified["files"]) != CORE_FILES:
        raise ValueError("baseline allowlist drift")
    if set(b_verified["files"]) != CORE_FILES | TREATMENT_FILES:
        raise ValueError("treatment allowlist must add only PAT/ANTI")
    if canonical_text(baseline_dir / "TASK.md") != canonical_text(treatment_dir / "TASK.md"):
        raise ValueError("task contract drift")
    if a_manifest["controls"] != b_manifest["controls"]:
        raise ValueError("experiment control drift")
    if _result_without_arm_metadata(baseline_dir / "result-template.json") != _result_without_arm_metadata(treatment_dir / "result-template.json"):
        raise ValueError("result schema or budget drift")
    project_root = treatment_dir.parents[1]
    sources = b_manifest.get("knowledge_sources", {})
    if set(sources) != TREATMENT_FILES:
        raise ValueError("treatment knowledge source mapping drift")
    for bundled, source in sources.items():
        if canonical_text(treatment_dir / bundled) != canonical_text(project_root / source):
            raise ValueError(f"knowledge snapshot drift: {bundled}")
    return {
        "decision": "paired_packets_valid",
        "task_sha256": digest(canonical_text(baseline_dir / "TASK.md")),
        "controls_equal": True,
        "result_schema_equal_except_arm_metadata": True,
        "treatment_additions": sorted(TREATMENT_FILES),
        "baseline_context_sha256": a_verified["allowed_context_sha256"],
        "treatment_context_sha256": b_verified["allowed_context_sha256"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seal, preflight or compare a FATHER experiment")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("packet_dir", type=Path)
    build = sub.add_parser("build")
    build.add_argument("packet_dir", type=Path)
    build.add_argument("output", type=Path)
    preflight = sub.add_parser("preflight")
    preflight.add_argument("packet_dir", type=Path)
    preflight.add_argument("inventory", type=Path)
    compare = sub.add_parser("compare")
    compare.add_argument("baseline_dir", type=Path)
    compare.add_argument("treatment_dir", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        result = verify_packet(args.packet_dir)
    elif args.command == "build":
        result = build_packet(args.packet_dir, args.output)
    elif args.command == "compare":
        result = compare_arms(args.baseline_dir, args.treatment_dir)
    else:
        result = preflight_inventory(args.packet_dir, json.loads(args.inventory.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] != "preflight_fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
