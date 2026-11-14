# P1 VEC-S pgvector tuning pass

The first P1 VEC-S run produced:
- pgvector mean Recall@10 = 0.946667, min = 0.9, p95 ≈ 1.7062 ms;
- Qdrant mean Recall@10 = 0.96, min = 0.9, p95 ≈ 16.1785 ms.

The qualification threshold remains Recall@10 >= 0.95.

Therefore pgvector is not rejected. Its current HNSW configuration (ef_search=100) is marked as below the quality gate and must be tuned.

This tuning pass tests:

```text
ef_search = 100, 150, 200, 300, 400
```

For each value it records:
- mean/min Recall@10;
- p50/p95/p99 latency;
- the first minimum configuration that passes the recall threshold.

The selected configuration is the lowest ef_search value that satisfies the quality gate. This preserves the FATHER rule: meet quality first, then minimize operational/performance cost.

Run:

```powershell
.\scripts\brain_storage_bench_p1_pgvector_tuning.ps1
```
