# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. role-only admission — rejected: role is assertion, not evidence.
2. duplicate C0-C6 evaluator inside father-chassis — rejected: creates two truth engines.
3. direct hard import of Trust internals throughout orchestrator — rejected: excessive coupling.
4. CompetencyAdmissionGate + Trust adapter boundary — selected.

Algorithm:
1. orchestrator identifies next stage and owner agent;
2. gate loads stage competency policy;
3. adapter obtains Claim + EvidenceRecord set from Trust source;
4. call existing CompetencyEvaluator.qualify();
5. verify claim domain/capability matches stage policy;
6. qualified=false -> BLOCK;
7. qualified=true -> issue AdmissionDecision with qualification/evidence refs;
8. execute only when role ownership AND competency admission both pass.

Complexity:
policy lookup O(1); evaluation O(n evidence for claim).

Rationale:
reuse one evidence engine and keep dependency direction clean.