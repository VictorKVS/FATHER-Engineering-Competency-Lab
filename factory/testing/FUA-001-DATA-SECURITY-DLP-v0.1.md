# FUA-001 Data Security & DLP Gate v0.1

Status: IMPLEMENTED / CI VALIDATION REQUIRED

## 26.14 Input Validation

26.14.01 input must have expected type
26.14.02 oversized text is rejected
26.14.03 credential-like patterns are classified before routing

## 26.17 DLP

26.17.01 API-key-like content
26.17.02 password-like content
26.17.03 secret-like content
26.17.04 bearer-token-like content

Detected credential-like data is classified as CREDENTIAL and is not eligible for remote-model routing.

## Limit

Pattern detection is an initial deterministic layer, not a complete DLP product.
Production requires broader classifiers, structured secret detection, false-positive evaluation and policy integration.
