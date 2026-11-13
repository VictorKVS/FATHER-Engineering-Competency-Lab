# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. filename/title identity — rejected.
2. URL-only identity — rejected.
3. source_id + metadata + SHA-256 content fingerprint — selected.
4. content-addressed global object store — future storage layer.

Algorithm v1:
1. validate source metadata;
2. normalize source_class/title/locator/version;
3. compute SHA-256 when bytes are available;
4. create immutable SourceIntakeRecord;
5. compare hash to registry for duplicate-content signal;
6. never merge records automatically;
7. emit intake decision/evidence.

Complexity:
hashing O(n bytes); reference registry lookup O(1).