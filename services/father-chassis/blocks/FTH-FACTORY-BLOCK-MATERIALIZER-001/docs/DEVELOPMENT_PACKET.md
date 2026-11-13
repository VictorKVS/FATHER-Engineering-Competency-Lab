# DEVELOPMENT_PACKET

Authorized:
- deterministic filesystem materializer;
- SHA-256 tree integrity;
- qualification gate;
- EMBEDDED_COPY and binding-only modes;
- manifest evidence.

Forbidden in v1:
- remote downloads;
- package registries;
- container registry mutation;
- privileged installation;
- deployment to external hosts.

Files:
- src/father/factory/block_materializer.py
- tests/test_block_materializer.py
- scripts/g7_block_materializer_qualification_test.ps1
