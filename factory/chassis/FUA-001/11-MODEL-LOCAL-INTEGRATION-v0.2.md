# FUA-001 / 11.Model Router — Local Model Integration v0.2

Status: IMPLEMENTED_FOR_DISCOVERY_TEST

## 11.15 Supported local discovery transports

11.15.01 Ollama
- default endpoint: http://127.0.0.1:11434
- discovery: GET /api/tags
- chat: POST /api/chat

11.15.02 OpenAI-compatible local server
- probes:
  - http://127.0.0.1:8000/v1
  - http://127.0.0.1:1234/v1
  - http://127.0.0.1:8080/v1
- discovery: GET /models
- chat: POST /chat/completions

## 11.16 Architecture rule

FUA core is independent from a particular model host.
Transport-specific behavior is isolated in adapters.

## 11.17 Next proof

- discover a real model on target EVM;
- invoke it;
- record latency and response;
- run a controlled FUA mission using the real model;
- preserve readiness DENIED until compatibility/security tests pass.
