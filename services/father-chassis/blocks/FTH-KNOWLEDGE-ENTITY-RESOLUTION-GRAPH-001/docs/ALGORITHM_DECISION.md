# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. merge by raw name only — rejected.
2. embedding similarity auto-merge — deferred.
3. exact normalized name + same type deterministic merge — selected for v1.
4. human-reviewed probabilistic resolution — future adapter.

Algorithm v1:
1. validate extraction sets and referential integrity;
2. flatten entities in stable extraction-set/entity order;
3. normalize canonical name by trim + Unicode casefold key;
4. key by (entity_type, normalized_name);
5. merge exact-key entities; union source entity IDs/evidence chunks;
6. detect same normalized name across different types as explicit conflict;
7. map source entity IDs -> node IDs;
8. rewrite source relations into graph edges;
9. deduplicate exact relation tuple deterministically while unioning lineage;
10. calculate node/edge/snapshot hashes from stable semantic inputs.

Complexity O(E + R) expected with hash maps.