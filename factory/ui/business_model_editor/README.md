# FATHER Business Model Editor v0.1

## Два режима входа

### 1. Import Diagram
Пользователь загружает готовую схему из редактора или изображение/экспорт:
- BPMN XML
- SVG
- PNG/JPG
- PDF
- draw.io / diagrams.net export
- Mermaid / PlantUML
- JSON/YAML модели FATHER

Pipeline:
IMPORT
→ PARSE / VISION
→ DETECT ELEMENTS
→ DETECT CONNECTIONS
→ MAP TO FATHER BUSINESS MODEL
→ FIND AMBIGUITIES
→ ASK ONLY CRITICAL QUESTIONS
→ NORMALIZE
→ RENDER AS EDITABLE DIAGRAM

### 2. Build from Description
Пользователь описывает процесс текстом.

Pipeline:
TEXT
→ INTENT ANALYSIS
→ ACTORS
→ ACTIVITIES
→ INPUTS / OUTPUTS
→ DECISIONS
→ INFORMATION FLOWS
→ SYSTEMS / DOCUMENTS
→ GAPS / AMBIGUITIES
→ MODEL
→ EDITABLE DIAGRAM

## Главный принцип
Импортированная картинка никогда не становится конечным источником истины.
После импорта должна появиться machine-readable модель, которую можно редактировать, тестировать и экспортировать.

## Business Model Objects
- Actor / Role
- Organization
- Human Specialist
- AI Agent
- External System
- Application
- Document
- Data Object
- Data Store
- Start Event
- End Event
- Task
- Subprocess
- Decision / Gateway
- Message Flow
- Sequence Flow
- API Flow
- Human Approval
- Timer
- Error
- Gate
- KPI / Metric
- Risk
- Security Boundary
- Note / Annotation

## Editor Requirements
- drag & drop
- snap/grid
- zoom/pan
- multi-select
- group/ungroup
- swimlanes
- connectors
- auto-layout
- icon palette
- search
- mini-map
- undo/redo
- version history
- comments
- validation
- import/export
- drill-down
- inspector panel

## Exports
- FATHER JSON/YAML
- BPMN 2.x
- SVG
- PNG
- PDF
- Mermaid
- PlantUML
- API / information-flow contracts
