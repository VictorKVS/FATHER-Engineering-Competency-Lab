# FATHER Factory — BPMN L1 v0.1

## Назначение
Декомпозиция общего L0 процесса фабрики на управляемые подпроцессы цехов.

## Pool: FATHER Factory

### Lane: Customer
- Start Event: Idea / Need
- Submit Request
- Review Clarification
- Approve Business Intent
- Accept / Reject Final Product

### Lane: ALINA / Factory Supervisor
- Register Order
- Assign Product ID
- Route to Workshop
- Monitor Gates
- Manage Rework
- Freeze Release Candidate
- Route to Polygon
- Route to Acceptance
- Store Factory Experience

### Lane: Business Analysis
- Interpret Intent
- Resolve Ambiguities
- Define Scope
- Build SIPOC
- Build BPMN
- Define Roles
- Define Information Flows
- Define Business Rules
- Define Acceptance Criteria
- Business Gate

### Lane: System Analysis
- Derive Functional Requirements
- Derive Non-Functional Requirements
- Define Systems / Boundaries
- Define Interfaces
- Define Events
- Define Data Exchanges
- System Gate

### Lane: Architecture
- Select Architecture Pattern
- Assign Responsibilities
- Define Components
- Define Integration Topology
- Define Deployment Assumptions
- Architecture Gate

### Lane: Data & Knowledge
- Define Data Model
- Define Knowledge Sources
- Define RAG / Graph
- Define Provenance
- Define Lifecycle
- Data Gate

### Lane: AI / LLM Design
- Define AI Capabilities
- Select Model Roles
- Define Prompt Contracts
- Define Context Strategy
- Define Evaluation
- Define Fallback
- AI Gate

### Lane: Security
- Define Trust Boundaries
- Build Threat Model
- Define Security Controls
- Define Policies
- Define Security Tests
- Security Gate

### Lane: Development
- Select Reusable Blocks
- Generate / Implement Missing Blocks
- Integrate Components
- Build Artifact
- Build Gate

### Lane: QA
- Unit Tests
- Integration Tests
- Functional Tests
- Regression Tests
- AI Eval
- Quality Gate

### Lane: DevSecOps
- Build Pipeline
- SBOM
- Container / Package
- Deployment Candidate
- Observability Setup

### Lane: Optimization
- A/B Candidates
- Compare Metrics
- Select Best Known Configuration
- Regression Recheck

### Lane: Polygon
- Receive Frozen RC
- Adversarial Tests
- Failure / Chaos
- Load / Recovery
- Security Exercises
- PASS / FAIL

### Lane: Release
- Acceptance Package
- Release Package
- Deployment
- Sale / Delivery
- Support Handoff

## Main Sequence
Start
→ Register Order
→ Business Analysis
→ G1
→ System Analysis
→ Architecture
→ G2
→ Data & Knowledge
→ AI / LLM
→ Security
→ Development
→ G3
→ QA
→ G4
→ DevSecOps
→ Optimization
→ Freeze RC
→ Polygon
→ G5
→ Acceptance
→ Release
→ Production Experience
→ End / Learning Loop

## Rework gateways
- Business ambiguity → Business Analysis
- Missing system requirement → Business Analysis / System Analysis
- Architecture inconsistency → Architecture
- Security failure → Security / Architecture / Development
- QA failure → Development
- Optimization regression → AI / Architecture / Development
- Polygon failure → relevant upstream workshop
- Acceptance rejection → relevant upstream workshop
