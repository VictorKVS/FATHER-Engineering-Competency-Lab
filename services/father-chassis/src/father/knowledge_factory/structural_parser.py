from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from father.knowledge_factory.legal_provenance import (
    ProvenanceRecord,
    SourceAdmissibilityDecision,
    verify_provenance_binding,
)
from father.knowledge_factory.source_intake import SourceIntakeRecord


def _canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class StructuralParseRequest:
    intake: SourceIntakeRecord
    decision: SourceAdmissibilityDecision
    provenance: ProvenanceRecord
    content_bytes: bytes
    media_type: str


@dataclass(frozen=True, slots=True)
class StructuralUnit:
    unit_id: str
    ordinal: int
    unit_type: str
    text: str
    locator: str
    source_id: str
    source_content_hash: str


@dataclass(frozen=True, slots=True)
class StructuralDocument:
    document_id: str
    source_id: str
    source_content_hash: str
    provenance_id: str
    parser_id: str
    parser_version: str
    units: tuple[StructuralUnit, ...]
    document_hash: str


@dataclass(frozen=True, slots=True)
class StructuralParseDecision:
    status: str
    document: StructuralDocument | None
    diagnostics: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class DeterministicTextStructuralParser:
    parser_id = "FTH-TEXT-STRUCTURAL-PARSER"
    parser_version = "1.0.0"
    supported_media_types = frozenset({"text/plain", "text/markdown"})

    @staticmethod
    def _is_heading(line: str) -> bool:
        stripped = line.strip()
        if stripped.startswith("#"):
            return True
        if stripped and len(stripped) <= 120 and stripped.upper() == stripped:
            letters = [ch for ch in stripped if ch.isalpha()]
            return bool(letters)
        return False

    @staticmethod
    def _flush_paragraph(
        units: list[StructuralUnit],
        paragraph_lines: list[tuple[int, str]],
        source_id: str,
        source_hash: str,
    ) -> None:
        if not paragraph_lines:
            return
        start = paragraph_lines[0][0]
        end = paragraph_lines[-1][0]
        text = " ".join(value.strip() for _, value in paragraph_lines).strip()
        if text:
            ordinal = len(units)
            units.append(
                StructuralUnit(
                    unit_id=f"UNIT-{ordinal:06d}",
                    ordinal=ordinal,
                    unit_type="paragraph",
                    text=text,
                    locator=f"line:{start}-{end}",
                    source_id=source_id,
                    source_content_hash=source_hash,
                )
            )
        paragraph_lines.clear()

    def parse(self, request: StructuralParseRequest) -> StructuralParseDecision:
        if request.decision.status != "APPROVED":
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=(
                    f"source decision is not APPROVED: {request.decision.status}",
                ),
            )

        provenance_errors = verify_provenance_binding(
            request.intake,
            request.decision,
            request.provenance,
        )
        if provenance_errors:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=tuple(
                    f"provenance: {error}" for error in provenance_errors
                ),
            )

        if request.media_type not in self.supported_media_types:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=(f"unsupported media_type: {request.media_type}",),
            )

        if request.intake.content_hash is None:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=("source content hash is required",),
            )

        actual_hash = sha256(request.content_bytes).hexdigest()
        if actual_hash != request.intake.content_hash:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=("content bytes do not match intake content_hash",),
            )

        try:
            text = request.content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=(f"invalid UTF-8: {exc}",),
            )

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        units: list[StructuralUnit] = []
        paragraph_lines: list[tuple[int, str]] = []

        for line_no, line in enumerate(lines, start=1):
            if not line.strip():
                self._flush_paragraph(
                    units,
                    paragraph_lines,
                    request.intake.source_id,
                    request.intake.content_hash,
                )
                continue

            if self._is_heading(line):
                self._flush_paragraph(
                    units,
                    paragraph_lines,
                    request.intake.source_id,
                    request.intake.content_hash,
                )
                ordinal = len(units)
                units.append(
                    StructuralUnit(
                        unit_id=f"UNIT-{ordinal:06d}",
                        ordinal=ordinal,
                        unit_type="heading",
                        text=line.strip(),
                        locator=f"line:{line_no}-{line_no}",
                        source_id=request.intake.source_id,
                        source_content_hash=request.intake.content_hash,
                    )
                )
            else:
                paragraph_lines.append((line_no, line))

        self._flush_paragraph(
            units,
            paragraph_lines,
            request.intake.source_id,
            request.intake.content_hash,
        )

        if not units:
            return StructuralParseDecision(
                status="REJECTED",
                document=None,
                diagnostics=("source contains no structural text units",),
            )

        hash_payload = {
            "source_id": request.intake.source_id,
            "source_content_hash": request.intake.content_hash,
            "provenance_id": request.provenance.provenance_id,
            "parser_id": self.parser_id,
            "parser_version": self.parser_version,
            "units": [asdict(unit) for unit in units],
        }
        document_hash = sha256(_canonical(hash_payload).encode("utf-8")).hexdigest()
        document = StructuralDocument(
            document_id=f"DOC-{document_hash[:16]}",
            source_id=request.intake.source_id,
            source_content_hash=request.intake.content_hash,
            provenance_id=request.provenance.provenance_id,
            parser_id=self.parser_id,
            parser_version=self.parser_version,
            units=tuple(units),
            document_hash=document_hash,
        )
        return StructuralParseDecision(
            status="PARSED",
            document=document,
            evidence_refs=(
                f"source-sha256:{request.intake.content_hash}",
                f"document-sha256:{document_hash}",
                f"provenance:{request.provenance.provenance_id}",
            ),
        )
