# FUA-001 Ollama Windows Settings Repair v0.3

Background

Current Ollama Windows desktop releases may persist their own model location in:
%LOCALAPPDATA%\Ollama\db.sqlite

Recent Windows reports show this persisted desktop setting can override or conflict with OLLAMA_MODELS.

Procedure

1. inspect actual PID owning 11434;
2. inspect user/machine OLLAMA_MODELS values;
3. inspect db.sqlite read-only;
4. inspect server.log for the effective OLLAMA_MODELS value;
5. before repair, stop Ollama;
6. back up db.sqlite;
7. replace only persisted values that clearly reference an Ollama models path;
8. persist matching user OLLAMA_MODELS;
9. restart on loopback;
10. verify /api/tags and FUA discovery.

Safety

- database is backed up first;
- source model store is never modified;
- no model is downloaded;
- no model is deleted;
- no external network listener is configured;
- if no unambiguous persisted path is found, repair exits without forcing a schema assumption.
