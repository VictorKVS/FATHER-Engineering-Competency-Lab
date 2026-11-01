# FUA-001 Stage 2 — Kubernetes Deployment & Operational Validation v0.1

Stage 1 flight certification is complete for the DOCKER_CONTAINED_ONLY profile.

Stage 2 goal: prove that the certified FUA-001 container profile can be deployed,
operated, recovered, observed and security-tested under Kubernetes without weakening
the Stage 1 security boundary.

## Stage 2 gates

- 2.01 KUBERNETES PREFLIGHT / CLUSTER READY
- 2.02 FUA IMAGE & LOCAL REGISTRY PATH
- 2.03 NAMESPACE / DEPLOYMENT / SERVICE
- 2.04 CONFIGMAP / SECRET BOUNDARY
- 2.05 RESOURCES / SECURITYCONTEXT
- 2.06 PROBES / SELF-HEALING
- 2.07 NETWORKPOLICY DEFAULT DENY
- 2.08 OBSERVABILITY
- 2.09 ROLLING UPDATE / ROLLBACK
- 2.10 FAILURE / NODE-POD RECOVERY
- 2.11 KUBERNETES SECURITY POLYGON
- 2.12 KUBERNETES CERTIFICATION REVIEW

## Certified base inherited from Stage 1

- production state: PRODUCTION_RELEASED
- approved execution profile: DOCKER_CONTAINED_ONLY
- Windows host native execution: NOT_APPROVED
- Stage 1 flight certification: PASS

## 2.01 acceptance

PASS requires:
- Docker Engine reachable;
- minikube available;
- kubectl available;
- profile otus-k8s exists or can be started non-destructively with Docker driver;
- Kubernetes API reachable;
- node Ready;
- kube-system core workloads available;
- kubectl context bound to otus-k8s.

No delete/reset/recreate is permitted in 2.01.
