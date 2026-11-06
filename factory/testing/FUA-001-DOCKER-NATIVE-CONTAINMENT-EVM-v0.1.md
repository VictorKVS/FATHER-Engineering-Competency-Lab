# FUA-001 Docker Native Containment EVM v0.1

Production execution profile for untrusted/native code.

Required controls:
- Docker isolation boundary;
- network=none;
- read-only root filesystem;
- all Linux capabilities dropped;
- no-new-privileges;
- non-root UID/GID;
- no host mounts;
- bounded tmpfs only;
- memory limit 256 MiB;
- CPU limit 1 core;
- PID limit 32.

This profile is an alternative production trust boundary when the Windows host
cannot prove a Restricted Token / AppContainer / Low Integrity execution boundary.

PASS applies only to the Docker-contained execution profile. It does not certify
arbitrary native execution directly on the Windows host.
