from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re

from father.knowledge_factory.structural_parser import StructuralDocument, StructuralUnit


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True, slots=True)
class ChunkPolicy:
    policy_id: str
    version: str
    max_chars: int = 1200
    include_heading_context: bool = True
    overlap_chars: int = 0

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("policy version is required")
        if self.max_chars <= 0:
            errors.append("max_chars must be positive")
        if self.overlap_chars != 0:
            errors.append("overlap_chars must be 0 in v1")
        return tuple(errors)


@dataclass(frozen=True, slots=True)
class NormalizedChunk:
    chunk_id: str
    ordinal: int
    text: str
    chunk_hash: str
    source_id: str
    document_id: str
    document_hash: str
    source_unit_ids: tuple[str, ...]
    source_locators: tuple[str, ...]
    policy_id: str
    policy_version: str


@dataclass(frozen=True, slots=True)
class NormalizedChunkSet:
    chunk_set_id: str
    source_id: str
    document_id: str
    document_hash: str
    normalizer_id: str
    normalizer_version: str
    policy_id: str
    policy_version: str
    chunks: tuple[NormalizedChunk, ...]
    chunk_set_hash: str


@dataclass(frozen=True, slots=True)
class ChunkingDecision:
    status: str
    chunk_set: NormalizedChunkSet | None
    diagnostics: tuple[str, ...] = ()


class DeterministicStructuralChunker:
    normalizer_id = "FTH-DETERMINISTIC-NORMALIZER"
    normalizer_version = "1.0.0"

    @staticmethod
    def _validate_document(document: StructuralDocument) -> tuple[str, ...]:
        errors: list[str] = []
        expected = list(range(len(document.units)))
        actual = [unit.ordinal for unit in document.units]
        if actual != expected:
            errors.append("structural unit ordinals are not contiguous")
        for unit in document.units:
            if unit.source_id != document.source_id:
                errors.append(f"unit {unit.unit_id} source_id mismatch")
            if unit.source_content_hash != document.source_content_hash:
                errors.append(f"unit {unit.unit_id} source_content_hash mismatch")
            if not unit.text.strip():
                errors.append(f"unit {unit.unit_id} is empty")
        return tuple(errors)

    @staticmethod
    def _split_text(text: str, max_chars: int) -> tuple[str, ...]:
        normalized = _normalize_ws(text)
        if not normalized:
            return ()
        if len(normalized) <= max_chars:
            return (normalized,)

        words = normalized.split(" ")
        parts: list[str] = []
        current: list[str] = []
        current_len = 0
        for word in words:
            if len(word) > max_chars:
                if current:
                    parts.append(" ".join(current))
                    current = []
                    current_len = 0
                for start in range(0, len(word), max_chars):
                    parts.append(word[start:start + max_chars])
                continue

            addition = len(word) if not current else len(word) + 1
            if current and current_len + addition > max_chars:
                parts.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += addition
        if current:
            parts.append(" ".join(current))
        return tuple(part for part in parts if part)

    @classmethod
    def _chunk_hash(
        cls,
        *,
        document: StructuralDocument,
        policy: ChunkPolicy,
        text: str,
        unit_ids: tuple[str, ...],
        locators: tuple[str, ...],
    ) -> str:
        payload = {
            "source_id": document.source_id,
            "document_id": document.document_id,
            "document_hash": document.document_hash,
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "normalizer_id": cls.normalizer_id,
            "normalizer_version": cls.normalizer_version,
            "text": text,
            "source_unit_ids": unit_ids,
            "source_locators": locators,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()

    def chunk(
        self,
        document: StructuralDocument,
        policy: ChunkPolicy,
    ) -> ChunkingDecision:
        diagnostics = list(policy.validate())
        diagnostics.extend(self._validate_document(document))
        if diagnostics:
            return ChunkingDecision("REJECTED", None, tuple(diagnostics))

        chunks: list[NormalizedChunk] = []
        current_heading: StructuralUnit | None = None
        current_text_parts: list[str] = []
        current_unit_ids: list[str] = []
        current_locators: list[str] = []

        def flush() -> None:
            if not current_text_parts:
                return
            text = _normalize_ws(" ".join(current_text_parts))
            if not text:
                current_text_parts.clear()
                current_unit_ids.clear()
                current_locators.clear()
                return
            ordinal = len(chunks)
            unit_ids = tuple(dict.fromkeys(current_unit_ids))
            locators = tuple(dict.fromkeys(current_locators))
            chunk_hash = self._chunk_hash(
                document=document,
                policy=policy,
                text=text,
                unit_ids=unit_ids,
                locators=locators,
            )
            chunks.append(
                NormalizedChunk(
                    chunk_id=f"CHK-{chunk_hash[:16]}",
                    ordinal=ordinal,
                    text=text,
                    chunk_hash=chunk_hash,
                    source_id=document.source_id,
                    document_id=document.document_id,
                    document_hash=document.document_hash,
                    source_unit_ids=unit_ids,
                    source_locators=locators,
                    policy_id=policy.policy_id,
                    policy_version=policy.version,
                )
            )
            current_text_parts.clear()
            current_unit_ids.clear()
            current_locators.clear()

        for unit in document.units:
            normalized = _normalize_ws(unit.text)
            if not normalized:
                continue

            if unit.unit_type == "heading":
                flush()
                current_heading = unit
                continue

            pieces = self._split_text(normalized, policy.max_chars)
            for piece in pieces:
                prefix = ""
                heading_id: str | None = None
                heading_locator: str | None = None
                if policy.include_heading_context and current_heading is not None:
                    prefix = _normalize_ws(current_heading.text)
                    heading_id = current_heading.unit_id
                    heading_locator = current_heading.locator

                candidate = piece if not prefix else f"{prefix}\n{piece}"
                candidate = _normalize_ws(candidate)

                if len(candidate) > policy.max_chars:
                    flush()
                    if prefix:
                        available = policy.max_chars - len(prefix) - 1
                        if available <= 0:
                            prefix = ""
                            heading_id = None
                            heading_locator = None
                            available = policy.max_chars
                        subpieces = self._split_text(piece, available)
                    else:
                        subpieces = self._split_text(piece, policy.max_chars)

                    for subpiece in subpieces:
                        text = subpiece if not prefix else f"{prefix}\n{subpiece}"
                        text = _normalize_ws(text)
                        ordinal = len(chunks)
                        ids = tuple(
                            x for x in (heading_id, unit.unit_id) if x is not None
                        )
                        locs = tuple(
                            x for x in (heading_locator, unit.locator) if x is not None
                        )
                        chunk_hash = self._chunk_hash(
                            document=document,
                            policy=policy,
                            text=text,
                            unit_ids=ids,
                            locators=locs,
                        )
                        chunks.append(
                            NormalizedChunk(
                                chunk_id=f"CHK-{chunk_hash[:16]}",
                                ordinal=ordinal,
                                text=text,
                                chunk_hash=chunk_hash,
                                source_id=document.source_id,
                                document_id=document.document_id,
                                document_hash=document.document_hash,
                                source_unit_ids=ids,
                                source_locators=locs,
                                policy_id=policy.policy_id,
                                policy_version=policy.version,
                            )
                        )
                    continue

                projected = _normalize_ws(" ".join(current_text_parts + [candidate]))
                if current_text_parts and len(projected) > policy.max_chars:
                    flush()

                if not current_text_parts and prefix:
                    current_text_parts.append(prefix)
                    current_unit_ids.append(current_heading.unit_id)
                    current_locators.append(current_heading.locator)

                current_text_parts.append(piece)
                current_unit_ids.append(unit.unit_id)
                current_locators.append(unit.locator)

        flush()

        if not chunks:
            return ChunkingDecision(
                "REJECTED",
                None,
                ("no normalized chunks produced",),
            )

        set_payload = {
            "source_id": document.source_id,
            "document_id": document.document_id,
            "document_hash": document.document_hash,
            "normalizer_id": self.normalizer_id,
            "normalizer_version": self.normalizer_version,
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "chunk_hashes": [chunk.chunk_hash for chunk in chunks],
        }
        set_hash = sha256(_canonical(set_payload).encode("utf-8")).hexdigest()
        chunk_set = NormalizedChunkSet(
            chunk_set_id=f"CHSET-{set_hash[:16]}",
            source_id=document.source_id,
            document_id=document.document_id,
            document_hash=document.document_hash,
            normalizer_id=self.normalizer_id,
            normalizer_version=self.normalizer_version,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            chunks=tuple(chunks),
            chunk_set_hash=set_hash,
        )
        return ChunkingDecision("CHUNKED", chunk_set)
