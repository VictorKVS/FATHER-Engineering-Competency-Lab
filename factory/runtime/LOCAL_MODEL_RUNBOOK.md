# Local Model Runbook

## Goal
Run a discovered GGUF model behind a local HTTP chat-completions endpoint and execute the same FATHER stage contract used by other providers.

## Preferred path
Use a local llama.cpp-compatible server. FATHER talks only to the HTTP contract; model files remain local.

## Candidate order for first Stage 000 run
1. GigaChat3-10B-A1.8B-Q4_K_S
2. Qwen2.5-14B-Instruct-1M-Q4_K_M
3. GigaChat-20B-A3B-v1.5-Q4_K_M

## Server contract
Expected endpoint:
`http://127.0.0.1:8080/v1/chat/completions`

Expected model endpoint for preflight:
`http://127.0.0.1:8080/v1/models`

## FATHER command
`father-factory run-stage --stage factory/stages/STAGE_000_IDEA.yaml --input examples/father_stage000_input.yaml --adapter local-http --endpoint http://127.0.0.1:8080/v1/chat/completions --model local-gguf --run-type LOCAL_LLM --evidence-dir .father/runs`

## PASS evidence
- server reachable
- stage output parses as JSON
- required output fields present
- run record persisted
- hashes and latency recorded

Do not promote a model from this smoke run. Promotion requires the same-input A/B/N protocol and eval/security gates.

## Target-host proven path (2026-10-29)

Detected executable:
`C:\\Users\\1\\AppData\\Local\\Microsoft\\WinGet\\Packages\\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\\llama-server.EXE`

First candidate model:
`C:\\Users\\1\\.lmstudio\\models\\bartowski\\ai-sage_GigaChat3-10B-A1.8B-GGUF\\ai-sage_GigaChat3-10B-A1.8B-Q4_K_S.gguf`

PowerShell launch example:

`& 'C:\\Users\\1\\AppData\\Local\\Microsoft\\WinGet\\Packages\\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\\llama-server.EXE' -m 'C:\\Users\\1\\.lmstudio\\models\\bartowski\\ai-sage_GigaChat3-10B-A1.8B-GGUF\\ai-sage_GigaChat3-10B-A1.8B-Q4_K_S.gguf' --host 127.0.0.1 --port 8080 -ngl 99 -c 8192`

After startup verify:
`Invoke-RestMethod http://127.0.0.1:8080/v1/models`

Then execute Stage 000:
`father-factory run-stage --stage factory/stages/STAGE_000_IDEA.yaml --input examples/father_stage000_input.yaml --adapter local-http --endpoint http://127.0.0.1:8080/v1/chat/completions --model local-gigachat3-10b --run-type LOCAL_LLM --evidence-dir .father/runs`


## Runtime security baseline

The first target-host launch exposed a llama.cpp warning:
- CORS allowed all origins;
- no API key was configured.

For FATHER local same-machine use, the baseline must therefore be:

`--host 127.0.0.1 --cors-origins localhost`

Authentication should be added with one of:
- `--api-key <secret>`
- `--api-key-file <path>`

Secrets must never be committed to Git.

A 503 response from `/v1/models` with message `Loading model` means the HTTP server is alive but model initialization is incomplete. This state is `STARTING`, not `FAILED`.

State mapping:
- connection refused -> SERVER_DOWN
- HTTP 503 Loading model -> STARTING
- HTTP 200 /v1/models -> READY
- model request schema failure -> RUNTIME_CONTRACT_FAIL
- inference failure -> MODEL_RUNTIME_FAIL
