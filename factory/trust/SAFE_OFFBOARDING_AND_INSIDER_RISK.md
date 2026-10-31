# Safe Offboarding and Insider-Risk Canon

FATHER must remain safe when an employee, contractor, administrator or maintainer leaves the project.

This control exists to prevent both accidental lockout and malicious retaliation.

## Required offboarding sequence

1. Register the offboarding event.
2. Transfer ownership of repositories, cloud resources, domains, registries and secrets.
3. Inventory all credentials, tokens, SSH keys, signing keys and service accounts touched by the person.
4. Revoke personal access.
5. Rotate shared or potentially exposed credentials.
6. Verify branch protection and administrator recovery.
7. Verify production access and break-glass ownership.
8. Verify CI/CD runners, webhooks, bots and integrations.
9. Verify model/API credentials and external connectors.
10. Verify backups and restore path.
11. Run integrity comparison against known-good release manifests.
12. Run security regression and audit.
13. Record evidence and close the offboarding gate.

## Explicitly prohibited design

FATHER must not contain:
- revenge logic;
- time bombs;
- destructive kill switches controlled by one developer;
- hidden account lockouts;
- logic that deletes data after employment termination;
- secret backdoors;
- logic that punishes an organization or users if a person is removed.

A heartbeat or license failure may move the system to a safe restricted mode, but must not destroy data, encrypt assets, sabotage production or retaliate.

## Continuity principle

No single maintainer must be indispensable for recovery.

At least two independent authorized recovery paths must exist for critical systems.

## Insider-risk response

Suspicious behavior triggers:
DETECT → LIMIT PRIVILEGES → PRESERVE EVIDENCE → REVIEW → ROTATE → RESTORE KNOWN GOOD → RETEST.

Not retaliation.
