# FUA-001 Stage 2.01B — WSL2 Kubernetes Preflight

## Decision

Windows-host Minikube with the Docker/KIC driver is blocked on the target workstation
by repeated Windows icacls failure while preparing the Minikube SSH key.

Stage 2 therefore uses WSL2-native Minikube inside Ubuntu-22.04 while retaining
Docker Desktop as the Docker provider through WSL integration.

## Boundary

- Windows-host Minikube: BLOCKED_BY_HOST_TOOLING
- WSL2 distro: Ubuntu-22.04
- Minikube profile: otus-k8s
- Driver: docker
- Container runtime: containerd
- CPU: 4
- Memory: 6144 MiB
- FUA production security profile remains DOCKER_CONTAINED_ONLY

## Acceptance

PASS requires:
- Docker available from Ubuntu-22.04;
- Linux minikube v1.39.0 available;
- Linux kubectl v1.37.1 available;
- otus-k8s starts with Docker driver;
- Kubernetes API responds;
- node reaches Ready;
- kube-system workloads are queryable.
