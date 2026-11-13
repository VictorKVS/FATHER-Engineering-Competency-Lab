# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. fixed raw character windows — rejected.
2. LLM semantic chunking — deferred.
3. structural-unit-aware deterministic chunking — selected.
4. tokenizer-aware model-specific chunking — future adapter.

Algorithm v1:
1. validate StructuralDocument units/order/binding;
2. normalize whitespace per unit;
3. track latest heading as section context;
4. append paragraphs while max_chars allows;
5. flush before overflow;
6. oversize paragraph split deterministically by word boundaries;
7. preserve source_unit_ids/locators;
8. compute chunk_hash from stable document/policy/text/lineage;
9. emit ordered NormalizedChunkSet.

Complexity O(total text length).