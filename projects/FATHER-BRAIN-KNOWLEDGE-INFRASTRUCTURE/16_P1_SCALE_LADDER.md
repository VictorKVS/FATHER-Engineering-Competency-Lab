# P1 Scale Ladder — M / L / XL

The same benchmark contract is extended without changing the qualification meaning.

| Profile | Records / vectors | Status |
|---|---:|---|
| S | 10,000 | measured |
| M | 100,000 | next |
| L | 1,000,000 | planned after M |
| XL | 10,000,000 | planned after L |

## Invariants

- vector dimensions: 384;
- top-k: 10;
- Recall@10 gate: >= 0.95;
- pgvector S operating point baseline: HNSW ef_search=300;
- concurrency: C1/C4/C16;
- deterministic seed: 20261114;
- image digest and evidence hash required.

## Exact reference optimization

The deterministic vector generator maps IDs onto a unit circle using a modular permutation.

For M/L/XL the multiplier is coprime with the corpus size, therefore exact nearest neighbors can be recovered from neighboring angular positions using a modular inverse.

This changes reference computation from O(N) per query to O(K), preventing the benchmark itself from becoming the bottleneck at 1M/10M.

## Resource-limit rule

A failed large profile due to RAM/disk/index limits is not hidden or retried until it passes.

It becomes evidence:

```text
candidate
profile
last qualified size
first failed size
failure class
resource state
configuration
```

That boundary is useful input for Storage Selection Engine.

## Commands

Start with M:

```powershell
.\scripts\brain_storage_bench_p1_scale.ps1 M all
```

Then, only after M evidence is analyzed:

```powershell
.\scripts\brain_storage_bench_p1_scale.ps1 L all
```

XL is the 10M qualification attempt:

```powershell
.\scripts\brain_storage_bench_p1_scale.ps1 XL all
```

Do not skip M/L: the purpose is to discover scaling breakpoints, not merely to reach the largest number.
