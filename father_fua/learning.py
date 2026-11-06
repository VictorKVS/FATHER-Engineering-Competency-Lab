from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class LearningProposal:
    proposal_id: str
    kind: str
    content: str
    provenance: str
    approved: bool = False


class LearningGate:
    def approve(self, proposal: LearningProposal, *, external_approval: bool) -> LearningProposal:
        if not external_approval:
            raise PermissionError("external approval required")
        return LearningProposal(
            proposal_id=proposal.proposal_id,
            kind=proposal.kind,
            content=proposal.content,
            provenance=proposal.provenance,
            approved=True,
        )
