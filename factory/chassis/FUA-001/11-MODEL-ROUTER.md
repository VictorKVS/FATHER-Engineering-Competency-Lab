# FUA-001 / 11.Model Router — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 11.01 Purpose

Select an approved model by capability, privacy, cost and availability without embedding provider-specific business logic in the agent core.

## 11.02 Required fields

11.01 Model Registry
11.02 Provider Adapter
11.03 Local Model Adapter
11.04 Remote Model Adapter
11.05 Capability Profile
11.06 Context Profile
11.07 Cost Profile
11.08 Latency Profile
11.09 Privacy Profile
11.10 Security Profile
11.11 Task-to-Model Routing
11.12 Fallback
11.13 Health Check
11.14 Model Regression

## 11.03 Model contract

Every model profile exposes:
model_id, provider, local_or_remote, context_window, structured_output,
tool_calling, embeddings, reasoning_profile, latency_profile, cost_profile,
privacy_profile, safety_profile, supported_modalities, health_check.

## 11.04 Draft tests

MODEL-T001 choose capable model
MODEL-T002 reject unhealthy model
MODEL-T003 local-only privacy blocks remote
MODEL-T004 budget filters expensive model
MODEL-T005 context requirement filters small model
MODEL-T006 fallback to next approved model
MODEL-T020 unapproved model never selected
MODEL-T021 privacy policy overrides cost/performance convenience
MODEL-T030 model replacement preserves core contract

## 11.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
