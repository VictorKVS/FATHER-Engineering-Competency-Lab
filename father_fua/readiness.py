from __future__ import annotations


MANDATORY = (
    "FUNCTIONAL","INTEGRATION","SECURITY","PERFORMANCE","COST",
    "RELIABILITY","REGRESSION","EVIDENCE","HUMAN_ACCEPTANCE",
)


def release_decision(gates: dict[str,str]) -> str:
    for name in MANDATORY:
        if gates.get(name) != "PASS":
            return "DENIED"
    return "PASS"
