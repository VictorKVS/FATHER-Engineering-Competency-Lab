# FUA-001 / 26.Security Operating Layer — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 26.01 Purpose
Apply mandatory horizontal security controls across every FUA block and specialization.

## 26.02 Required fields
26.01 Identity & Authentication
26.02 Authorization
26.03 Least Privilege
26.04 Secrets Management
26.05 Data Classification
26.06 Encryption
26.07 Network Security
26.08 Supply Chain Security
26.09 Prompt Injection Defense
26.10 RAG Poisoning Defense
26.11 Tool Abuse Defense
26.12 Model Abuse Defense
26.13 Memory Poisoning Defense
26.14 Input Validation
26.15 Output Validation
26.16 Malware / File Inspection
26.17 DLP
26.18 SIEM Integration
26.19 Incident Response
26.20 Threat Intelligence
26.21 Vulnerability Management
26.22 Red Team
26.23 Compliance
26.24 Security Evidence
26.25 Security Release Gate

## 26.03 Invariants
- deny by default;
- least privilege;
- open HIGH/CRITICAL security finding blocks release;
- security controls emit evidence;
- no component can opt out of this layer.

## 26.04 Current decision
BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
