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

## v0.2 SID handling correction

The first target-EVM run showed that icacls did not resolve the raw SID token in /deny and returned a name/SID mapping error.

The runner now:
- passes the trustee as *SID, which is icacls numeric-SID form;
- verifies the resulting ACL text contains the current SID before executing the denial probe;
- removes the deny ACE using the same numeric-SID form during cleanup.
## v0.3 ACL display-name correction

The target EVM confirmed that icacls accepted the numeric *SID trustee but displayed the resulting ACE using the resolved account name (for example DESKTOP-...\\user) rather than the literal SID.

The runner now verifies:
- current WindowsIdentity.Name is present in the ACL output;
- the matching ACE includes (DENY)(M);
- only then proceeds to the real write-denial probe.
## v0.4 sentinel verification order

The target EVM proved the child write was denied with PermissionError. The same directory deny ACE also prevented the parent PowerShell process from reading the sentinel before cleanup.

The runner now:
- treats the child PermissionError as the OS-enforced write-denial proof;
- removes only the temporary deny ACE;
- reads the sentinel afterward and requires ORIGINAL;
- then performs the final ACL reset and directory cleanup.