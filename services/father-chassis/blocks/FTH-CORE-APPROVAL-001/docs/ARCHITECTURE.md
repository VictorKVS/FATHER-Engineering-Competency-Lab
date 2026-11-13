# Architecture
Owner: Principal/Solution Architect.

FactoryExecutor / ChassisRuntime
        -> HumanApprovalGate
             -> local cache + RLock
             -> StateStore(namespace=approval_gate)
                    -> SQLite / PostgreSQL

Human operator -> approve(approval_id) -> HumanApprovalGate.

Responsibilities:
- ApprovalGate owns approval lifecycle semantics;
- Runtime owns execution;
- StateStore owns persistence only.

Security boundary:
agent may request approval; agent reasoning is never authority.

Scaling limit:
RLock is process-local; distributed coordination is future work.