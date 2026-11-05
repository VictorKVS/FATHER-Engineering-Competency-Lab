# FATHER Book Ingestion & Translation Contract v1

## Goal
One agent must ingest books in common ebook/document formats, preserve source structure, detect language, optionally translate, and produce a canonical representation for RAG/Narrative KB.

## Supported format classes

### Native text / markup
- .txt
- .md
- .html / .htm
- .fb2
- .xml

### Office / document
- .docx
- .pdf

### Ebook containers
- .epub

### Converter-backed
- .mobi
- .azw
- .azw3

MOBI/AZW/AZW3 are accepted through an external conversion adapter such as Calibre when available. They must not be silently rejected.

## PDF modes
1. Text PDF: extract embedded text and page boundaries.
2. Scanned/image PDF: send pages to vision/OCR adapter.
3. Mixed PDF: combine text layer with visual extraction.

## Mandatory source preservation
Never overwrite the original book.

For every extracted chunk preserve when available:
- source_file
- source_format
- source_language
- chapter
- section
- page
- paragraph
- character offsets
- extraction_method
- source_hash

## Language handling
Pipeline:
BOOK -> EXTRACT -> LANGUAGE DETECT -> ORIGINAL CANONICAL TEXT -> optional TRANSLATION -> ALIGNMENT -> RAG/KB

Rules:
- detect language per book and, when needed, per chunk;
- preserve original text;
- translated text is stored separately;
- each translated chunk must reference its original chunk_id;
- names, terminology and quoted phrases should be protected from uncontrolled translation;
- uncertain translations must be marked, not invented.

## Canonical chunk
Each logical chunk should be representable as:

{
  "chunk_id": "...",
  "source_file": "...",
  "format": "epub",
  "language": "en",
  "chapter": "...",
  "page": null,
  "text_original": "...",
  "translation": {
    "target_language": "ru",
    "text": "...",
    "model": "...",
    "status": "translated"
  },
  "media": [],
  "source_hash": "..."
}

## Images, maps, tables, footnotes
Do not discard non-text content.

Store:
- illustrations
- maps
- diagrams
- tables
- captions
- footnotes/endnotes
- embedded metadata

Visual items should receive stable ids and links back to chapter/page/section.

## Benchmark rule
For model comparison:
- all models receive the same extracted canonical text;
- all models receive the same retrieval results;
- translation is a separate benchmark dimension;
- do not mix parser quality with LLM quality.

## Acceptance tests
A Book Reader agent is not APPROVED until it passes:
1. TXT
2. EPUB
3. FB2
4. PDF text
5. PDF scanned/image
6. DOCX
7. MOBI/AZW3 through converter path
8. non-Russian source
9. mixed-language source
10. book with footnotes/table/image

## Output products
- canonical_book.json
- chunks.jsonl
- media_manifest.json
- translation_alignment.jsonl
- extraction_report.json
- evidence.json
