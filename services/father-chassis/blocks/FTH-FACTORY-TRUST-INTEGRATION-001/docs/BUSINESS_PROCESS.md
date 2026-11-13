# Business Process
Owner: Senior Business Analyst.

Goal:
ensure Competency Admission can consume authoritative Trust functions reproducibly in developer, CI and qualification environments.

Before:
Trust exists as a sibling project but chassis does not declare or install it.

After:
one documented installation/version contract provides the same Trust API locally and in CI.

KPIs:
- import path hacks: 0;
- environment-specific hidden dependencies: 0;
- chassis+Trust tests runnable from declared toolchain: 100%;
- incompatible Trust API detected before runtime: 100%.