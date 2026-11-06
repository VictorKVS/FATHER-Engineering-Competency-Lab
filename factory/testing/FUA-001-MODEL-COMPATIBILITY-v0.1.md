# FUA-001 Model Compatibility Gate v0.1

## 23.10 Purpose

Convert model discovery into an explicit compatibility decision.

## 23.11 Mandatory checks

23.11.01 local execution requirement
23.11.02 endpoint health
23.11.03 chat capability
23.11.04 approved transport
23.11.05 non-empty prompt
23.11.06 bounded prompt size

## 23.12 Decision

Unknown or failed requirement => DENY.
Discovery alone never equals compatibility approval.

## 23.13 Next extension after target model discovery

- identify actual model ID and runtime;
- measure response latency;
- verify output non-empty;
- record prompt/response hashes;
- execute controlled mission;
- create model-specific compatibility evidence.
