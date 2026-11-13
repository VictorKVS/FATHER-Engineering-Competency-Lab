# Evidence & Provenance

Evidence records support claims.

## Minimum evidence record

```json
{
  "evidence_id": "EVD-...",
  "subject_id": "SUBJECT-...",
  "claim_id": "CLM-...",
  "evidence_type": "test",
  "artifact_ref": "...",
  "artifact_hash": "...",
  "source_commit": "...",
  "observed_at": "...",
  "issuer": "...",
  "signature_ref": null,
  "parent_evidence_hash": null
}
```

## Intended chain

```text
CLAIM
  -> EVIDENCE
  -> HASH
  -> SIGNATURE / IDENTITY
  -> QUALIFICATION DECISION
```

The ledger should be append-oriented. Corrections create new records; historical evidence is not silently rewritten.
