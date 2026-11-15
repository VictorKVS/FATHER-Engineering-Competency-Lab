# P1-M v2 pgvector minimum-cost operating point

Scale Corpus v2 validated the lowest tested HNSW configuration.

## Selected configuration

```text
m = 16
ef_construction = 64
ef_search = 64
Recall@10 mean = 0.963333
p95 = 2.1579 ms
index build = 31.3226 s
```

This configuration passes the current quality gate `Recall@10 >= 0.95`.

## Architectural decision

For the L=1,000,000 qualification step, pgvector starts from this minimum-cost passing profile rather than the previous heavy profile:

```text
old: m=48 / ef_construction=512 / ef_search=1000
new: m=16 / ef_construction=64 / ef_search=64
```

The previous heavy profile achieved higher quality margin but imposed excessive build cost on M.

## Important caveat

The observed `recall_at_k_min = 0.1` means some individual queries performed poorly even though mean Recall@10 passed.

Therefore the L result must preserve:
- mean Recall@10;
- minimum Recall@10;
- latency;
- build time;
- resource use.

A future qualification contract may add a minimum per-query recall gate if required by the product SLA.
