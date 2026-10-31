# Agent Threat Model V1

The agent is treated as a security boundary, not merely as an LLM wrapper.

## Trust boundaries

1. User/task input
2. Retrieved RAG content
3. Knowledge base
4. Model endpoint
5. Tools/MCP/services
6. Memory/state
7. Output consumer
8. Evidence/logging store

## Mandatory threats to test

- prompt injection from user input
- indirect prompt injection from retrieved documents
- unauthorized tool invocation
- secret leakage
- sensitive data over-collection
- malicious or malformed model output
- model endpoint substitution
- poisoned knowledge source
- excessive permissions
- uncontrolled network access
- infinite/repeated tool loops
- denial of service/resource exhaustion
- evidence tampering
- dependency/supply-chain compromise

## Rule

Any agent release candidate must have explicit controls and evidence for applicable threats.
