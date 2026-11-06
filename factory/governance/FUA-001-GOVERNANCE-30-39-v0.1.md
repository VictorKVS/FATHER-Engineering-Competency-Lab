# FUA-001 Governance Runtime Baseline 30-39

Status: IMPLEMENTED AS VALIDATION BASELINE

## 30 Data Governance
Typed data policies: classification, retention, encryption, readers/writers.

## 31 Configuration / Secrets
Governance rule: SECRET != CONFIG. Deployment profiles require an explicit secrets backend.

## 32 Deployment Profiles
LOCAL_DEV, LOCAL_GPU, WORKSTATION, DOCKER, KUBERNETES, CLOUD, AIR_GAPPED, EDGE.

AIR_GAPPED requires:
- network_mode = NONE
- remote_models_allowed = false

## 33-36 Lifecycle
Sensitive changes to model/prompt/knowledge/policy/tool/skill/security baseline require recertification.

## 37 Multi-Agent
Same platform does not imply trust.
Delegation requires authenticated peers and explicit capability authorization.

## 38 Event / Message Bus
Baseline provides correlation, sequence, idempotency and dead-letter support.

## 39 Identity / Authorization
Agent trust record includes authentication, authorized capabilities and autonomy level.

## Current limitation
This is an executable governance validation baseline, not the complete production control plane.
