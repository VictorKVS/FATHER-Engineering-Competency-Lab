# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- import hijacking through sys.path;
- wrong Trust package version;
- copied/forked evaluator divergence;
- CI tests chassis without Trust;
- Trust changes break admission silently.

Controls:
- public package import only;
- no path mutation;
- explicit bootstrap;
- joint CI;
- independent Trust tests;
- compatibility test on public API;
- fail-closed admission if Trust unavailable.

Future:
signed package artifacts, internal index, lockfile/hash pinning.