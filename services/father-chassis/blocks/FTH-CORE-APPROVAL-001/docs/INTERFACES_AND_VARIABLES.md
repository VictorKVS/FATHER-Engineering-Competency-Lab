# Interfaces and Variables
Owner: Architect + System Analyst.

request(trace_id: str, action: str) -> ApprovalRecord

check(trace_id: str, action: str, approval_id: str|None)
- action not protected -> return;
- valid approved matching ID -> return;
- missing ID -> create pending + raise ApprovalRequired;
- invalid/unapproved/mismatched ID -> PermissionError.

approve(approval_id: str) -> ApprovalRecord
Transition: PENDING -> APPROVED.

get(approval_id: str) -> ApprovalRecord
Unknown -> KeyError.

ApprovalRecord fields:
- approval_id: UUID string;
- trace_id: str;
- action: str;
- status: "pending"|"approved".

Persistence:
namespace=approval_gate
key=approval_id.