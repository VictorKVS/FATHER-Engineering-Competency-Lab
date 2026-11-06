# FUA-001 Ollama Model Store Rebind v0.1

Purpose: repair a target-EVM state where Ollama is listening on 127.0.0.1:11434 but /api/tags returns zero models even though Ollama manifests exist on disk.

Target model store:
F:\FATHER_MODELS\ollama

Procedure:
1. verify manifests and blobs;
2. stop existing Ollama process;
3. set OLLAMA_MODELS to the explicit FATHER model root;
4. bind Ollama to loopback only;
5. start ollama serve;
6. verify /api/tags and ollama list;
7. verify FUA discovery.

Safety:
- no model download;
- no model deletion;
- no manifest rewrite;
- no external listening address;
- process restart only.

If manifests exist but blobs are absent/incomplete, the runner returns a blocked state rather than downloading anything automatically.
