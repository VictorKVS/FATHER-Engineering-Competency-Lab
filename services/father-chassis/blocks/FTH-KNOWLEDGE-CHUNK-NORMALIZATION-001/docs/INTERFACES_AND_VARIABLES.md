# Interfaces and Variables
Owner: Architect + System Analyst.

ChunkPolicy:
- policy_id: str
- version: str
- max_chars: int
- include_heading_context: bool
- overlap_chars: int

NormalizedChunk:
- chunk_id: str
- ordinal: int
- text: str
- chunk_hash: str
- source_id: str
- document_id: str
- document_hash: str
- source_unit_ids: tuple[str,...]
- source_locators: tuple[str,...]
- policy_id: str
- policy_version: str

NormalizedChunkSet:
- chunk_set_id: str
- source_id: str
- document_id: str
- document_hash: str
- normalizer_id: str
- normalizer_version: str
- policy_id: str
- policy_version: str
- chunks: tuple[NormalizedChunk,...]
- chunk_set_hash: str

ChunkingDecision:
- status: CHUNKED|REJECTED
- chunk_set: NormalizedChunkSet|None
- diagnostics: tuple[str,...]