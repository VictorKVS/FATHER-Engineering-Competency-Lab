# EVID-FUA-K8S-02-IMAGE-0032

## Gate
FUA-001 Stage 2.02 — Kubernetes Image

## Result
PASS

## Image
- tag: `father/fua-001:k8s-0.1`
- image id: `sha256:5284548677c011010b1bc8190a1520c6613d2c2a8c19bd21f75d2bd493459480`
- runtime user: `10001:10001`
- runtime UID observed: `10001`

## Container verification
- build: PASS
- non-root: PASS
- read-only root filesystem: PASS
- tmpfs /tmp: PASS
- capabilities drop ALL: PASS
- no-new-privileges: PASS
- memory limit 256 MiB: PASS
- health endpoint: PASS
- health response: `{"status":"ok","version":"0.1.0"}`

## Minikube transfer
- cluster profile: `otus-k8s`
- image load: PASS
- image present in Minikube image store: PASS

## Boundary
This gate proves image build/runtime/load only.
Kubernetes Deployment, Service, workload SecurityContext, probes and policies are not yet certified.

## Next
2.03_DEPLOYMENT_SERVICE
