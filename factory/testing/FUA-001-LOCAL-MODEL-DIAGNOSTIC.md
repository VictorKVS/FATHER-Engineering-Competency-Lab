# FUA-001 Local Model Environment Diagnostic

Purpose: distinguish four states on the target workstation.

01. Model runtime running and models discoverable.
02. Runtime installed but not running.
03. Model files exist but no compatible serving runtime is active.
04. No usable local model environment is present.

The diagnostic is read-only.
It checks known processes, executables, loopback listening ports, FUA discovery and candidate model roots.

It does not install, delete, move or modify model files.
