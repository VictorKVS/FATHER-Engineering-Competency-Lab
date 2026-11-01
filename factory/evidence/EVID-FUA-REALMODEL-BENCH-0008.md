# FUA-001 Evidence Record — REAL MODEL BENCHMARK 0008

Evidence ID: EVID-FUA-REALMODEL-BENCH-0008
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Model

Model: qwen2.5:7b
Transport: OLLAMA
Endpoint: http://127.0.0.1:11434

## 02. Runs

Run 1: PASS, audit=true, latency=787 ms, response_len=150
SHA256: 71fd979f1d5d33f3034b60d117f97a8ec22806ab6df8efa79ffccba27affd830

Run 2: PASS, audit=true, latency=1541 ms, response_len=514
SHA256: b4346647f64799cabc97d922e60655fecc6f5feadee3e301fc88f88a3bdf9b9a

Run 3: PASS, audit=true, latency=1239 ms, response_len=440
SHA256: d103be1f56e06ee019bbf6e8d804f7f7f545b1e4be3be11a00b253632414f159

Run 4: PASS, audit=true, latency=971 ms, response_len=334
SHA256: dcb88ca68eae40636b77744c58c9796c28d7b219fbb35f8c802188f8622f01e9

Run 5: PASS, audit=true, latency=1390 ms, response_len=492
SHA256: 0378f3f3bf03855c0abe4dc4b7342af4601322af1d4b80851b2fdba100b90281

## 03. Aggregate

COUNT: 5
SUCCESS_RATE: 1.000
AVG_MS: 1185
P50_MS: 1239
P95_MS: 1541
UNIQUE_HASHES: 5

## 04. Gate decision

REAL_MODEL_BENCHMARK: PASS
MODEL_STABILITY: PASS
AUDIT_CHAIN: PASS
STEADY_STATE_LATENCY: PASS

INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
