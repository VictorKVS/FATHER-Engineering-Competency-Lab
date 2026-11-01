# FUA-001 / 16.Skill Runtime — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 16.01 Purpose

Register and resolve versioned agent skills independently from permissions.

## 16.02 Required fields

16.01 Skill Registry
16.02 Skill Manifest
16.03 Skill Dependencies
16.04 Skill Permissions
16.05 Skill Selection
16.06 Skill Execution
16.07 Skill Versioning
16.08 Skill Tests

## 16.03 Invariants

- installed skill != permission;
- dependencies explicit;
- version required;
- policy decides execution.

## 16.04 Draft tests

SKILL-T001 register skill
SKILL-T002 dependency check
SKILL-T003 version required
SKILL-T004 select by capability
SKILL-T020 skill cannot grant itself permission

## 16.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
