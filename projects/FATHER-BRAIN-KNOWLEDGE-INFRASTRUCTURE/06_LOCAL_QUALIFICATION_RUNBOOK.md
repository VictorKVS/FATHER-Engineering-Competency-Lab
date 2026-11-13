# 06 — Local Qualification Runbook

## Purpose
Final gate for the first Brain Supply Resolver slice.

## Branch
`brain-knowledge-infrastructure-development`

## Run from
`G:\1\FATHER-Engineering-Competency-Lab\services\father-chassis`

## Commands

```powershell
git fetch origin
git switch brain-knowledge-infrastructure-development
git pull origin brain-knowledge-infrastructure-development
.\scripts\g7_brain_supply_qualification_test.ps1
```

## Expected checks

The harness must prove:

- Ruff passes;
- full chassis regression passes;
- Agent Class A* and Brain Class B* are independent;
- exact eligible package binds;
- wrong B-class blocked;
- incompatible A-class blocked;
- missing capability blocked;
- wrong domain/role/mode blocked;
- unauthorized classification blocked;
- cross-tenant binding blocked;
- revoked package blocked;
- ambiguity explicit;
- result independent of candidate order;
- policy version changes decision identity;
- no silent higher Brain Class fallback.

## PASS marker

```text
G7 BRAIN SUPPLY RESOLVER: PASS
```

## Evidence

The harness writes:

```text
artifacts\local\g7_brain_supply_qualification_YYYY-MM-DD.json
```

Only after this evidence is inspected may the block be promoted from qualification candidate to qualified.
