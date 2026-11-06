# FUA-001 Stage 2.03 — Deployment and Service

## Purpose
Deploy the already verified Stage 2.02 image into Kubernetes and prove workload/service wiring.

## Objects
- Namespace: `father-system`
- Deployment: `father-system/fua-001`
- Service: `father-system/fua-001` (ClusterIP)
- Image: `father/fua-001:k8s-0.1`
- Pull policy: `Never` (image is preloaded by Stage 2.02)

## Baseline safety
- service-account token automount disabled;
- non-root UID/GID 10001;
- no privilege escalation;
- read-only root filesystem;
- all Linux capabilities dropped;
- writable `/tmp` provided only as bounded emptyDir.

These settings are inherited safety defaults. Stage 2.05 performs the formal
resource/SecurityContext certification.

## Acceptance
PASS requires:
1. namespace applies;
2. deployment becomes Available;
3. pod is Running/Ready;
4. service exists and has at least one endpoint;
5. `GET /health` succeeds through the Kubernetes Service ClusterIP path from the pod.
