from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CompatibilityResult:
    compatible: bool
    reason: str

def check_chassis_compatibility(required: str, actual: str) -> CompatibilityResult:
    if not required.startswith("father-chassis"):
        return CompatibilityResult(False, "unsupported compatibility expression")
    if actual.startswith("1.0.0rc") or actual.startswith("0."):
        return CompatibilityResult(True, "compatible with RC baseline")
    return CompatibilityResult(False, f"incompatible chassis version: {actual}")
