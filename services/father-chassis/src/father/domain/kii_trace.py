from __future__ import annotations

from father.core.decision_trace import DecisionTrace

KII_STAGES = (
    "OBJECT_IDENTIFICATION",
    "NORM_SOURCE_SELECTION",
    "REQUIREMENT_EXTRACTION",
    "APPLICABILITY_ANALYSIS",
    "FACT_COLLECTION",
    "IMPACT_ANALYSIS",
    "CATEGORY_ASSESSMENT",
    "CONTROL_SELECTION",
    "IMPLEMENTATION_DECISION",
    "HUMAN_APPROVAL",
    "IMPLEMENTATION_EVIDENCE",
    "VERIFICATION",
    "PERIODIC_RECHECK",
)


def new_kii_decision(subject: str) -> DecisionTrace:
    return DecisionTrace.create(subject=subject, domain="KII")
