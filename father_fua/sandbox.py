from __future__ import annotations

import ntpath
from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxPolicy:
    network_allowed: bool = False
    max_seconds: int = 30
    max_output_bytes: int = 1_000_000
    allowed_roots: tuple[str, ...] = ()
    allowed_commands: tuple[str, ...] = ()


def _normalize_windows_path(path: str) -> str:
    if not path or "\x00" in path:
        raise ValueError("invalid path")
    p = path.replace("/", "\\")
    if p.startswith("\\\\") or p.startswith("\\?\\") or p.startswith("\\.\\"):
        raise ValueError("UNC/device paths are not allowed")
    drive, tail = ntpath.splitdrive(p)
    if not drive or not tail:
        raise ValueError("absolute drive path required")
    normalized = ntpath.normpath(p)
    if ".." in normalized.split("\\"):
        raise ValueError("path traversal is not allowed")
    return ntpath.normcase(normalized)


def validate_path(path: str, policy: SandboxPolicy) -> bool:
    try:
        candidate = _normalize_windows_path(path)
    except ValueError:
        return False

    for root in policy.allowed_roots:
        try:
            normalized_root = _normalize_windows_path(root)
            common = ntpath.commonpath([candidate, normalized_root])
        except (ValueError, OSError):
            continue
        if common == normalized_root:
            return True
    return False


def validate_command(command: str, policy: SandboxPolicy) -> bool:
    if not command or any(x in command for x in ("\n", "\r", "\x00")):
        return False
    executable = ntpath.basename(command.strip()).lower()
    allowed = {ntpath.basename(x).lower() for x in policy.allowed_commands}
    return executable in allowed


def validate_output_size(size_bytes: int, policy: SandboxPolicy) -> bool:
    return 0 <= size_bytes <= policy.max_output_bytes
