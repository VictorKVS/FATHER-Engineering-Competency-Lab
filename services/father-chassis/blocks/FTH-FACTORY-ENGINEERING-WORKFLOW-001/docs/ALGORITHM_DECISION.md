# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. event replay log — strongest auditability, higher implementation scope;
2. per-artifact/per-history keys — more writes and ordering complexity;
3. versioned workflow snapshot in StateStore — selected for current milestone.

Selected algorithm:
1. state changes only after validated admission;
2. serialize artifacts + history into canonical snapshot;
3. persist under namespace factory_engineering_workflow and key workflow_id;
4. on construction load snapshot;
5. reconstruct artifacts by typed factory;
6. recompute artifact hash and compare stored hash;
7. reconstruct history;
8. derive next stage from restored state.

Rationale:
minimal surface, deterministic recovery, compatible with SQLite/PostgreSQL StateStore.

Future:
event-sourced ledger may replace snapshot for distributed/audit-heavy deployment.