# Security Model
Owner: Security Architect / DevSecOps.

Assets:
human authorization decision, action binding, trace binding.

Threats:
- agent self-approval;
- approval replay for wrong action;
- fabricated ID;
- loss after restart;
- protected execution without authority.

Controls:
- UUID approval identity;
- explicit state;
- exact action matching;
- fail-closed validation;
- persistent StateStore;
- runtime enforcement;
- audit/qualification evidence.

Missing controls:
approver identity/signature, expiry/revocation, MFA, organizational policy, quorum.