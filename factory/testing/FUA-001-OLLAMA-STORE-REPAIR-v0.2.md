# FUA-001 Ollama Store Repair v0.2

Observed target-EVM state:
- Ollama executable present.
- Ollama listens on 127.0.0.1:11434.
- F:\FATHER_MODELS\ollama contains 8 manifests and 33 blobs (~29.16 GB).
- Explicit OLLAMA_MODELS rebind still yields /api/tags = 0 models.

Interpretation:
The model data exists, but the current Ollama runtime is not indexing the external store.

Repair strategy:
1. validate every manifest digest against source blobs;
2. stop Ollama;
3. materialize the validated store into Ollama's default user store;
4. prefer hard links where Windows/filesystem permits, otherwise copy only missing blobs;
5. restart Ollama on loopback;
6. verify /api/tags, ollama list and FUA discovery.

No model download is performed.
No source model blob is modified or deleted.
