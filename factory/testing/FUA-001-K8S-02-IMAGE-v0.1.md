# FUA-001 Stage 2.02 — Kubernetes Image

## Purpose

Build and verify the FUA-001 API container image before Kubernetes deployment.

## Image contract

- tag: `father/fua-001:k8s-0.1`
- API: `father_fua.api:app`
- listen: `0.0.0.0:8080`
- health: `GET /health`
- runtime UID/GID: `10001:10001`
- no embedded secrets
- minimal build context via `.dockerignore`

## Acceptance

PASS requires:
1. image builds in the native Docker Engine inside Ubuntu-22.04;
2. image runtime user is non-root;
3. container starts and Docker health becomes healthy;
4. `GET /health` returns `status=ok`;
5. immutable image ID / repo digest metadata is recorded when available;
6. image is loaded into Minikube profile `otus-k8s`;
7. Minikube confirms the image exists.

This gate does not authorize Kubernetes workload deployment. Deployment,
Service, probes, SecurityContext and resource policy are Stage 2.03+.
