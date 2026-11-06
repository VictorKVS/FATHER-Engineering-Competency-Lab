# FATHER Factory — Business Model L0 v0.1

## Назначение
Верхнеуровневая бизнес-модель фабрики FATHER. Этот слой первым появляется на Assembly Table после постановки задачи и до детального проектирования отдельных цехов.

## Сквозной поток
CUSTOMER INTENT
→ INTAKE & FORMALIZATION
→ BUSINESS ANALYSIS
→ SYSTEM ANALYSIS
→ ARCHITECTURE
→ DATA & KNOWLEDGE
→ AI / LLM DESIGN
→ SECURITY DESIGN
→ DEVELOPMENT / ASSEMBLY
→ QA / TEST
→ DEVSECOPS
→ OPTIMIZATION / A-B
→ RELEASE CANDIDATE
→ POLYGON
→ ACCEPTANCE
→ RELEASE / SALE / DEPLOYMENT
→ PRODUCTION EXPERIENCE
→ FATHER EXPERIENCE / KNOWLEDGE

## Участники
- Customer
- ALINA / Factory Supervisor
- Business Analyst
- System Analyst
- Solution Architect
- Data / Knowledge Engineer
- AI / LLM Engineer
- Security Architect
- Developer
- QA Engineer
- DevSecOps Engineer
- Optimization Engine
- Polygon
- Release / Product Manager

## Производственные пакеты
- Customer Intent
- Business Design Package
- System Design Package
- Architecture Package
- Data & Knowledge Package
- AI Configuration Package
- Security Package
- Build Artifact
- Test Evidence
- Best Known Configuration
- Release Candidate
- Polygon Report
- Release Package

## Gates
- G0 INTENT READY
- G1 BUSINESS READY
- G2 SYSTEM / ARCHITECTURE READY
- G3 BUILD READY
- G4 FACTORY VERIFIED
- G5 POLYGON VERIFIED
- G6 RELEASE READY

## Rework loops
- System Analysis → Business Analysis
- Architecture → System Analysis
- Security → Architecture
- QA → Development
- DevSecOps → Development / Architecture
- Optimization → AI / LLM / Architecture
- Polygon → Security / Development / Architecture
- Acceptance → relevant upstream workshop

## Правило
Каждый переход между цехами выполняется только через формальный пакет с проверяемым контрактом. Нельзя передавать «понимание» только текстом или чатом.
