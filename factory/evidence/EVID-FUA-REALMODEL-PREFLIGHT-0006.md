# FUA-001 Evidence Record — REAL MODEL PREFLIGHT 0006

Evidence ID: EVID-FUA-REALMODEL-PREFLIGHT-0006
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Discovery

FUA discovered models: 8
Selected model: qwen2.5:7b
Transport: OLLAMA
Endpoint: http://127.0.0.1:11434

## 02. Runtime state

ALREADY_LOADED: qwen2.5:7b

## 03. Warm-up

Warm-up prompt expected: READY
Warm-up response: READY
Warm-up elapsed: 280 ms
Ollama load_duration: 2877600 ns
eval_count: 2
done: true

## 04. Gate decision

REAL_MODEL_DISCOVERY: PASS
MODEL_SELECTED: PASS
MODEL_LOADED: PASS
WARMUP_INFERENCE: PASS
OLLAMA_RUNTIME: PASS

NEXT:
- full FUA real-model mission
- model-specific compatibility evidence
- steady-state latency benchmark
- real-model POLYGON

INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
