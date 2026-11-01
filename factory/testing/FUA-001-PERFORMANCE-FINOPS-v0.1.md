# FUA-001 Performance / FinOps Measurement v0.1

Status: IMPLEMENTED

## 53 Performance
Records sample count, success rate, P50 and P95 latency.

## 54 Capacity
Target workstation sizing remains a separate evidence item.

## 55 FinOps
Samples can carry token and monetary cost.
SLO evaluation can enforce maximum P95 latency and maximum cost.

## Target-EVM runner
scripts/test-fua-performance.ps1

The runner measures 20 full assembly missions using the deterministic local stub.
Real-model latency/cost measurement is performed only after the real local model gate is available.
