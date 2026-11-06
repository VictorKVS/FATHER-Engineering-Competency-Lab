# FUA-001 Kubernetes 2.01 Recovery — stale Minikube profile

## Trigger
Use only when the otus-k8s profile has residual Minikube state but the machine
configuration file machines/otus-k8s/config.json is missing.

## Safety
- no global Minikube reset;
- only profile otus-k8s is targeted;
- residual files are copied to factory/evidence/k8s-recovery before deletion;
- destructive deletion is fail-closed behind -ApproveRecreateStaleProfile;
- cluster is recreated with Docker driver, 4 CPUs, 6144 MiB.

## Result
After recovery PASS, re-run scripts/test-fua-k8s-01-preflight-evm.ps1.


## Windows Docker-driver certificate hardening

Cluster creation pins valid API server certificate names:
- control-plane.minikube.internal
- localhost

This avoids fail-open reliance on an automatically generated empty certSAN observed on the target Windows/Docker environment.
