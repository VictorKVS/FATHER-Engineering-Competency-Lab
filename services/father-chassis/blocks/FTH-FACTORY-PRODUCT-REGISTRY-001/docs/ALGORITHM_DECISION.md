# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. memory-only dictionary — rejected: restart loss;
2. dedicated custom DB — rejected for current scope: duplicates StateStore;
3. shared StateStore namespace + local cache — selected;
4. external package registry — deferred.

Algorithm:
1. derive key product_id@version;
2. check local cache;
3. if absent read StateStore;
4. reconstruct ProductRegistration;
5. compare recipe_hash on register;
6. reject mismatch;
7. persist if absent;
8. return stable registration.

Complexity: cache O(1); persistence backend-dependent.
Decision rationale: reuse qualified chassis state and minimize coupling.