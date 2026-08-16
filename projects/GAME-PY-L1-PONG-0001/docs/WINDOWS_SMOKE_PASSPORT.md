# Windows GUI smoke passport

## Passport

| Field | Value |
|---|---|
| ID | `EVID-GUI-WIN-0001` |
| Version | 0.1.0 |
| Status | procedure ready; evidence not yet collected |
| Related | `GATE-PY-PONG-0001`, `BUILD-PY-PONG-0001`, `TEST-PY-PONG-0002` |

## What is being solved

Headless unit tests and CI cannot prove that a real Tkinter window opens, receives keyboard input and remains responsive on the target Windows machine. This procedure creates operator-attested evidence without confusing it with automated evidence.

## Alternatives and decision

- Trust Linux CI: rejected because it never opens the target Windows GUI.
- Instantiate a window on a hosted runner: rejected as insufficient evidence for visible rendering and human controls.
- Manual undocumented check: rejected because it is not reproducible or reviewable.
- Scripted preparation plus explicit operator checks: selected as the smallest honest M1 proof.

## Procedure

From the project directory in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_smoke.ps1
```

The script first runs the automated core tests, starts the actual game, asks the operator to verify every control and writes `evidence/EVID-PY-PONG-WINDOWS.json`. Review that JSON before committing it. A failed or partially completed checklist cannot pass M1.

## Constraints, risks and decision rule

The evidence is an operator attestation, not cryptographic proof. A future packaged build requires a separate smoke run against the packaged executable. Do not publish screenshots/GIFs until the real window has passed this check; media must correspond to the tested version.

