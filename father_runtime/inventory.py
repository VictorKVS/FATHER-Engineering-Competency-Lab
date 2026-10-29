from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess


def _run(args: list[str]) -> str | None:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=20, check=False)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def detect_ollama() -> list[dict]:
    if not shutil.which("ollama"):
        return []
    out = _run(["ollama", "list"])
    if not out:
        return []
    rows=[]
    for line in out.splitlines()[1:]:
        parts=line.split()
        if parts:
            rows.append({"provider":"LOCAL_OLLAMA","model":parts[0],"raw":line})
    return rows


def detect_gguf() -> list[dict]:
    roots=[]
    for env_name in ("FATHER_MODEL_DIR","FATHER_EXTRA_MODEL_DIR"):
        if os.getenv(env_name):
            roots.append(Path(os.environ[env_name]))
    roots.extend([Path("models"), Path("data/models")])

    seen=set()
    rows=[]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.gguf"):
            key=str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "provider":"LOCAL_LLAMA_CPP",
                "model":p.name,
                "path":str(p),
                "size_bytes":p.stat().st_size
            })
    return rows


def inventory() -> dict:
    return {
        "ollama": detect_ollama(),
        "gguf": detect_gguf(),
    }


def main() -> int:
    print(json.dumps(inventory(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
