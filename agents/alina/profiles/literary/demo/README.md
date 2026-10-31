# ALINA Literary Demo

This demo is embedded in the FATHER repository as the first reusable agent/model benchmark.

Pipeline:
`genre suite -> automatic model rotation -> ALINA Literary runtime -> evidence -> deterministic checks -> review bundle -> GitHub`

Default suite contains six short cases:
- fantasy
- thriller
- romance
- action
- science fiction
- mystery

Each continuation target is capped at approximately one page (450 words maximum by suite policy).

Four physically discovered local text models are enabled in the automatic matrix.

Expert review is deliberately separated from deterministic checks. The benchmark writes a review bundle with full provenance so a human/reference reviewer can assess outputs without losing who generated what.
