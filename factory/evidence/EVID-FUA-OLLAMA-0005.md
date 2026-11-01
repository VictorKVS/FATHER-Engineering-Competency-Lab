# FUA-001 Evidence Record — OLLAMA WINDOWS MODEL DISCOVERY 0005

Evidence ID: EVID-FUA-OLLAMA-0005
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Root cause

Ollama desktop persisted model location in:
%LOCALAPPDATA%\Ollama\db.sqlite

Persisted value:
C:\Users\1\.ollama\models

User environment expected:
F:\FATHER_MODELS\ollama

Server log confirmed effective runtime value was still:
OLLAMA_MODELS=C:\Users\1\.ollama\models

## 02. Repair

- settings DB backed up;
- persisted settings.models changed to F:\FATHER_MODELS\ollama;
- matching user OLLAMA_MODELS persisted;
- Ollama restarted on 127.0.0.1:11434.

## 03. Result

API model inventory: 8

Models:
- qwen3-vl:8b-instruct-q4_K_M
- llava:7b
- qwen2.5-coder:1.5b
- qwen2.5-coder:7b-instruct-q4_K_M
- qwen2.5:7b
- qwen2.5:3b
- deepseek-r1:7b
- llama3.2:1b

FUA discovery: 8
Transport: OLLAMA
Endpoint: http://127.0.0.1:11434

## 04. Gate decision

OLLAMA_MODEL_STORE: PASS
OLLAMA_WINDOWS_SETTINGS: PASS
OLLAMA_API_DISCOVERY: PASS
FUA_MODEL_DISCOVERY: PASS

REAL_MODEL_INFERENCE: NEXT
INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
