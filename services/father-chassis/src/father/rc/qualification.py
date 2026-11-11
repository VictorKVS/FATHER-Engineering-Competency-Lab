from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Callable

@dataclass
class CheckResult:
    name: str
    passed: bool
    details: dict

@dataclass
class RCReport:
    release: str
    checks: list[CheckResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> dict:
        return {
            "release": self.release,
            "passed": self.passed,
            "checks": [asdict(c) for c in self.checks],
        }

def run_checks(checks: list[tuple[str, Callable[[], dict]]]) -> RCReport:
    results: list[CheckResult] = []
    for name, fn in checks:
        try:
            details = fn() or {}
            passed = bool(details.pop("passed", True))
            results.append(CheckResult(name, passed, details))
        except Exception as exc:
            results.append(CheckResult(name, False, {"error": f"{type(exc).__name__}: {exc}"}))
    return RCReport("FATHER FACTORY 1.0 RC1", results)
