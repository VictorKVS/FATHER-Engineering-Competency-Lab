# FUA-001 Windows Filesystem ACL EVM v0.1

Purpose:
prove an OS-enforced NTFS write boundary for a controlled protected directory while preserving write access to the sandbox work directory.

Mechanism:
- requires elevated PowerShell;
- creates temporary work and protected directories under ProgramData;
- verifies the sandbox Python can write inside workdir;
- applies a temporary NTFS deny ACE for the current SID to the protected directory;
- requires a write attempt to the protected sentinel to fail;
- verifies the sentinel remains unchanged;
- removes the deny ACE, resets ACLs, and deletes temporary directories in finally.

PASS means FILESYSTEM_ACL_BASELINE only.

It does not prove:
- global filesystem confinement;
- restricted token/AppContainer;
- defense against privileged/native escape;
- container/VM isolation.
