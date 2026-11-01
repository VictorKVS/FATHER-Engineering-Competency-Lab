# FUA-001 / 10.Tool Runtime — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 10.01 Purpose

Execute external capabilities through explicit registry, permission, validation and sandbox boundaries.

## 10.02 Required fields

10.01 Tool Registry
10.02 MCP Registry
10.03 Tool Adapter
10.04 Tool Router
10.05 Input Validation
10.06 Output Validation
10.07 Permission Gate
10.08 Credential Broker
10.09 Sandbox
10.10 Rate Limit
10.11 Tool Audit
10.12 Tool Evidence

## 10.03 Invariants

- tool presence does not imply permission;
- tool execution requires allow decision;
- model cannot mint permissions or credentials;
- input/output schemas are validated;
- privileged tools default deny;
- execution emits audit/evidence.

## 10.04 Draft tests

TOOL-T001 register tool
TOOL-T002 allowed tool executes
TOOL-T003 denied tool does not execute
TOOL-T004 invalid input rejected
TOOL-T005 output schema validated
TOOL-T020 model claim cannot grant permission
TOOL-T021 credential is never returned to model payload
TOOL-T022 unknown tool denied
TOOL-T023 rate limit enforced
TOOL-T024 privileged action requires approval
TOOL-T030 audit record emitted
TOOL-T031 sandbox failure safe-stops
TOOL-T032 tool result remains untrusted data

## 10.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
