from __future__ import annotations

from hashlib import sha256

from father.core.access_control import AccessControl, ResourceContext, SubjectContext
from father.core.decision_trace import (
    DecisionEvidence,
    DecisionOption,
    NormReference,
)
from father.domain.kii_trace import new_kii_decision


class KIIDecisionEngine:
    """Minimal working vertical slice for KII compliance decisions.

    It does not encode Russian KII law itself. It proves the architecture:
    authorization -> normative reference -> evidence -> alternatives -> decision trace.
    """

    def __init__(self, access_control: AccessControl | None = None) -> None:
        self.access_control = access_control or AccessControl()

    def assess(
        self,
        *,
        subject: SubjectContext,
        resource: ResourceContext,
        object_id: str,
        object_facts: str,
        norm: NormReference,
        proposed_decision: str,
    ):
        access = self.access_control.authorize(
            subject=subject,
            resource=resource,
            permission="propose:decision",
        )
        if not access.allowed:
            raise PermissionError(access.reason)

        trace = new_kii_decision(object_id)

        evidence_id = "facts-" + sha256(object_facts.encode("utf-8")).hexdigest()[:16]
        trace.add_evidence(
            DecisionEvidence(
                evidence_id=evidence_id,
                source="object-facts",
                locator=object_id,
                content_hash=sha256(object_facts.encode("utf-8")).hexdigest(),
                summary=object_facts,
            )
        )

        s1 = trace.add_step(
            stage="OBJECT_IDENTIFICATION",
            actor_type="human_or_service",
            actor_id=subject.subject_id,
            statement=f"Object {object_id} admitted to KII assessment",
            evidence_ids=[evidence_id],
            confidence=1.0,
        )

        s2 = trace.add_step(
            stage="REQUIREMENT_EXTRACTION",
            actor_type="father-compliance",
            actor_id="father-kii-engine",
            statement=f"Normative requirement {norm.requirement_id} attached to assessment",
            norm_refs=[norm],
            input_step_ids=[s1.step_id],
            confidence=1.0,
        )

        s3 = trace.add_step(
            stage="APPLICABILITY_ANALYSIS",
            actor_type="father-compliance",
            actor_id="father-kii-engine",
            statement="Object facts are evaluated against the selected normative requirement",
            norm_refs=[norm],
            evidence_ids=[evidence_id],
            input_step_ids=[s1.step_id, s2.step_id],
            confidence=0.8,
        )

        options = [
            DecisionOption(
                option_id="apply",
                description=proposed_decision,
                benefits=("normative coverage", "traceability"),
                risks=("requires human validation",),
            ),
            DecisionOption(
                option_id="defer",
                description="Defer decision pending additional evidence",
                benefits=("avoids unsupported conclusion",),
                risks=("delays final assessment",),
            ),
        ]

        s4 = trace.add_step(
            stage="CATEGORY_ASSESSMENT",
            actor_type="father-compliance",
            actor_id="father-kii-engine",
            statement=proposed_decision,
            norm_refs=[norm],
            evidence_ids=[evidence_id],
            input_step_ids=[s3.step_id],
            options=options,
            selected_option_id="apply",
            confidence=0.8,
            requires_human_approval=True,
        )

        return {
            "access": {
                "allowed": access.allowed,
                "reason": access.reason,
                "matched_role": access.matched_role,
            },
            "decision_step_id": s4.step_id,
            "decision_trace": trace.to_dict(),
        }
