# Business Process
Owner: Senior Business Analyst.

Goal:
an agent may not perform professional work using an undefined, stale, unqualified or unverifiable knowledge base.

Rule:
ROLE says what the agent may do.
COMPETENCY proves the agent can do it.
QUALIFIED KB proves what knowledge release the agent is allowed to rely on.

Input:
agent contract, required KB IDs, available KB releases, release qualification evidence.

Output:
ADMIT or BLOCK plus exact release IDs/hashes/evidence references.

KPIs:
- missing required KB admitted: 0%;
- unqualified release admitted: 0%;
- release without provenance admitted: 0%;
- admission traceable to exact release hash: 100%.