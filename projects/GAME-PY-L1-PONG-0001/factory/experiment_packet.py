"""Seal and preflight isolated FATHER experiment packets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from typing import Any

FIXED_TIMESTAMP = (2026, 8, 16, 0, 0, 0)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_packet(packet_dir: Path) -> dict[str, Any]:
    manifest = json.loads((packet_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    actual: dict[str, str] = {}
    combined = bytearray()
    for name, expected in sorted(manifest["allowed_files"].items()):
        data = (packet_dir / name).read_bytes()
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
    manifest_data = (packet_dir / "MANIFEST.json").read_bytes()
    entries = [("MANIFEST.json", manifest_data)] + [
        (name, (packet_dir / name).read_bytes()) for name in sorted(verified["files"])
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seal or preflight a FATHER experiment")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("packet_dir", type=Path)
    build = sub.add_parser("build")
    build.add_argument("packet_dir", type=Path)
    build.add_argument("output", type=Path)
    preflight = sub.add_parser("preflight")
    preflight.add_argument("packet_dir", type=Path)
    preflight.add_argument("inventory", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        result = verify_packet(args.packet_dir)
    elif args.command == "build":
        result = build_packet(args.packet_dir, args.output)
    else:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        result = preflight_inventory(args.packet_dir, inventory)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] != "preflight_fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
