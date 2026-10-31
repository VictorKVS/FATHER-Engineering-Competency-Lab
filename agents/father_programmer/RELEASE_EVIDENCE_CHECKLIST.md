# FATHER Programmer — Release Evidence Checklist

## Source
- [ ] Exact repository and commit known
- [ ] Parent commit known
- [ ] Requirement / algorithm / ADR trace complete
- [ ] External source provenance recorded
- [ ] License refs recorded

## Build
- [ ] Build workflow/version recorded
- [ ] Builder identity recorded
- [ ] Dependency locks recorded
- [ ] Environment manifest recorded
- [ ] Artifact digest recorded
- [ ] SBOM generated and hashed
- [ ] Build provenance generated

## Verification
- [ ] Unit tests complete
- [ ] Contract tests complete
- [ ] Integration tests complete
- [ ] Security checks complete
- [ ] License compliance complete
- [ ] Reproducibility check complete or reason approved

## Attestations
- [ ] SOURCE_ATTESTATION
- [ ] BUILD_ATTESTATION
- [ ] TEST_ATTESTATION
- [ ] SECURITY_ATTESTATION
- [ ] LICENSE_ATTESTATION
- [ ] RELEASE_ATTESTATION

## Release
- [ ] Release manifest created
- [ ] Release identity/signature verified
- [ ] Rollback reference recorded
- [ ] Recovery path verified
- [ ] RELEASE_TRUST_GATE passed
