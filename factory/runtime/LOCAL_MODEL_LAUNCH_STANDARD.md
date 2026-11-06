# FATHER Local Model Launch Standard v1

## Goal
One canonical agent must be able to swap compatible local models without changing its prompt, RAG, KB, contracts or task.

## Layers
`MODEL FILE -> LAUNCH PROFILE -> SERVER READY -> INFERENCE READY -> AGENT CONTRACT -> EVIDENCE`

## llama.cpp baseline
- bind localhost only;
- one parallel slot for MVP;
- explicit context budget;
- GPU offload requested, with runtime failure captured;
- template is selected from catalog, with ordered fallbacks;
- server log is stored per model;
- never interpret process start as model readiness.

Baseline flags:
`--host 127.0.0.1 --port 8080 --cors-origins localhost -np 1 -c 4096 -ngl 99`

## Template strategy
1. primary template from model catalog;
2. model metadata template where compatible;
3. family fallback;
4. if template cannot initialize, mark TEMPLATE_FAIL and continue to next model.

Current family defaults:
- Qwen2.5 / Qwen2.5-Coder -> chatml;
- DeepSeek-Coder-V2 -> deepseek2, then deepseek;
- GigaChat / GigaChat3 -> gigachat, then metadata/chatml;

llama.cpp currently exposes built-in templates including chatml, deepseek/deepseek2 and gigachat.

## One-agent policy
AG-001 ALINA Literary tests every catalog entry marked ELIGIBLE or ELIGIBLE_EXPERIMENTAL.
Non-generative and multimodal-only assets remain catalogued but are not forced through a text-generation contract.

## Result states
- FILE_MISSING
- SERVER_START_FAIL
- TEMPLATE_FAIL
- READY
- INFERENCE_FAIL
- CONTRACT_FAIL
- PASS

Every state produces evidence. A failed model must not stop the catalog sweep.
