# AG-STORY-001 — First As-Built Prototype

The first executable agent package now contains:

- agent identity and immutable construct references
- input/output contracts
- swappable model slot
- deny-by-default permissions
- runtime policy
- secure-by-design baseline
- threat model
- AgentExecutor
- Model Tournament engine
- execution evidence writer

## Current gate

AS_BUILT_BASELINE = HOLD

This is intentional. The package structure is assembled, but the following still
require real integration evidence:

1. resolve real Prompt artifact/version;
2. resolve real RAG artifact/version;
3. resolve real Knowledge Base snapshot/version;
4. execute at least one real model through an adapter;
5. run security tests and record evidence.

No qualification or Polygon claim is permitted before these items pass.
