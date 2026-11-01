# FUA-001 Local Model Bootstrap v0.1

Purpose: move from "no service discovered" to a precise actionable state.

The runner:
1. detects Ollama and LM Studio installations;
2. checks loopback serving ports;
3. starts Ollama service automatically when the executable is present but port 11434 is closed;
4. asks FUA discovery for actually served models;
5. if none are served, performs a bounded read-only scan of known model stores;
6. returns one deterministic state:
   - SERVICE_AND_MODEL_READY
   - MODEL_ARTIFACTS_FOUND_BUT_NOT_SERVED
   - RUNTIME_FOUND_NO_SERVED_MODEL
   - NO_RUNTIME_NO_MODEL_FOUND

It does not download models, delete files, alter model stores, or expose a service outside loopback.
