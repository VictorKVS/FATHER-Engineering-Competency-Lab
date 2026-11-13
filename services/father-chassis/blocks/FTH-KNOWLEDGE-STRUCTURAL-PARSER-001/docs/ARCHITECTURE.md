# Architecture
Owner: Principal/Solution Architect.

K1 SourceIntakeRecord
+
K2 APPROVED Decision + Provenance
        ↓
StructuralParserGate
        ↓
ParserAdapter
        ├─ validate provenance binding
        ├─ decode/parse
        ├─ build locators
        ├─ diagnostics
        └─ canonical output hash
        ↓
StructuralDocument
        ↓
K4 Semantic Chunk / Normalization

Reference adapter:
DeterministicTextStructuralParser.