# FATHER Book Ingestion MVP-01

This MVP validates real local ingestion of TXT, FB2 and PDF books from:

`book_benchmark/input/`

It does not commit book contents to GitHub.

## Current implemented formats
- TXT, including UTF-8 and legacy Russian encodings such as CP1251
- FB2/XML with metadata and section extraction
- PDF embedded-text extraction with page boundaries

## PDF boundary
If a PDF has no usable embedded text, status becomes `VISION_OCR_REQUIRED`.
That is not silently treated as successful text extraction. Vision/OCR is the next adapter.

## Output
- `evidence/book_ingestion/canonical_books.json`
- `evidence/book_ingestion/chunks.jsonl`
- `evidence/book_ingestion/extraction_report.json`

Original files are preserved. Canonical chunks keep source file, format, language, chapter/page and character offsets.

## Run
```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_BOOK_INGESTION_MVP01.ps1
```

Next:
1. visual PDF/image adapter;
2. translation alignment;
3. EPUB/DOCX;
4. MOBI/AZW3 through Calibre;
5. all-model RAG/KB benchmark on canonical chunks.
