# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. Boolean request flag — rejected: no durable authority trail.
2. Memory-only approval token — rejected: lost on restart.
3. Persistent UUID ApprovalRecord — selected.
4. External workflow/approval engine — deferred until organizational workflows require it.

Algorithm:
1. protected action without ID -> create UUID pending record;
2. persist record;
3. raise ApprovalRequired;
4. human operator approves ID;
5. persist APPROVED state;
6. later execution loads record;
7. allow only if action matches and status=approved;
8. otherwise fail closed.

Complexity: logical O(1) lookup; persistence backend-dependent.