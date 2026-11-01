from __future__ import annotations


def security_gate(findings: list[dict]) -> str:
    for finding in findings:
        if finding.get("severity") in {"HIGH","CRITICAL"} and finding.get("status") != "CLOSED":
            return "DENY"
    return "ALLOW"
