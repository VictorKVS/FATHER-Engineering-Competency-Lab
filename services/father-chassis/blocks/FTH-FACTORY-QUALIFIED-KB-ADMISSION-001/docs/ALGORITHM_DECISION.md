# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. check only kb_id exists — rejected.
2. allow latest folder/index automatically — rejected.
3. versioned KnowledgeBaseRelease registry + fail-closed gate — selected.
4. remote schema/metadata service — deferred.

Algorithm:
1. resolve stage owner agent;
2. read required knowledge_bases from FactoryAgentContract;
3. for every required kb_id select configured release;
4. validate release kb_id/status/hash/source/provenance/retrieval evidence;
5. if any required KB fails -> BLOCK;
6. otherwise issue KnowledgeAdmissionDecision with release IDs/hashes/evidence refs;
7. workflow records decision trace before stage PASS.

Complexity: O(number of required KBs).

Rationale:
deterministic reproducibility and evidence trace without prematurely building full Knowledge Factory.