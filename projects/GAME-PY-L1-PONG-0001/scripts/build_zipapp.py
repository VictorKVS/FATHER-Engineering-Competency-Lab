"""Build a deterministic, dependency-free Python zip application."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
DIST = PROJECT / "dist"
ARCHIVE = DIST / "father-pong.pyz"
FIXED_TIMESTAMP = (2026, 8, 16, 0, 0, 0)


def _write_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def build() -> dict[str, object]:
    DIST.mkdir(exist_ok=True)
    entries: list[tuple[str, bytes]] = [
        ("__main__.py", b"from pong.app import main\nraise SystemExit(main())\n"),
        ("BUILD-INFO.json", json.dumps({
            "project_id": "GAME-PY-L1-PONG-0001",
            "version": "0.1.0-pre-alpha",
            "runtime": "Python 3.11+ with Tkinter",
            "standalone_executable": False,
        }, sort_keys=True, separators=(",", ":")).encode()),
        ("LICENSE", (PROJECT / "LICENSE").read_bytes()),
    ]
    for path in sorted((PROJECT / "pong").glob("*.py")):
        entries.append((f"pong/{path.name}", path.read_bytes()))

    with zipfile.ZipFile(ARCHIVE, "w") as archive:
        for name, data in sorted(entries):
            _write_entry(archive, name, data)

    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "0.1.0",
        "artifact_id": "BUILD-PY-PONG-0001",
        "project_id": "GAME-PY-L1-PONG-0001",
        "version": "0.1.0-pre-alpha",
        "file": ARCHIVE.name,
        "sha256": digest,
        "requires": "Python 3.11+ with Tkinter",
        "standalone_executable": False,
        "decision": "portable Python zipapp; not an OS-native executable",
    }
    (DIST / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True))
