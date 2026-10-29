# FATHER Programmer Algorithm

INPUT
→ locate model element
→ resolve requirements
→ resolve algorithms
→ resolve contracts
→ resolve security constraints
→ search reusable modules
→ choose implementation strategy
→ create code skeleton
→ implement smallest valid increment
→ static checks
→ unit tests
→ contract tests
→ integration tests
→ security checks
→ traceability verification
→ evidence pack
→ handoff to Test Engineer

Decision points:
- missing requirement → HOLD
- ambiguous algorithm → RETURN TO ANALYST
- contract conflict → RETURN TO SYSTEM/ARCHITECT
- security conflict → RETURN TO SECURITY
- reusable verified block exists → REUSE/WRAP before BUILD


Extended canonical sequence:

→ verify source/provenance
→ verify license and intended-use compatibility
→ verify dependency/security status
→ record provenance metadata
→ update SBOM
→ generate artifact hash/manifest
→ verify integrity/heartbeat behavior where applicable
→ verify rollback/recovery
→ attach evidence

Additional decision points:
- code origin cannot be established → HOLD / REVIEW
- approved license with satisfied obligations → CONTINUE
- license rights or obligations unresolved → HOLD / LICENSE REVIEW
- integrity mechanism is not fail-safe → REJECT IMPLEMENTATION
- recovery depends irreversibly on one person/account → HOLD
