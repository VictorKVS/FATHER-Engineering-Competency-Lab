from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from trust_competency.models import Claim, EvidenceRecord, Subject


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def import_g6_manifest(path: str | Path) -> tuple[Subject, Claim, tuple[EvidenceRecord, ...]]:
    """Import FATHER G6 qualification as PRODUCT competency evidence.

    The adapter depends on the manifest format, while trust_competency core remains FATHER-independent.
    """
    manifest_path = Path(path)
    data: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))

    subject = Subject(
        subject_id="FATHER-CHASSIS",
        subject_type="product",
        name="FATHER Chassis",
    )
    claim = Claim(
        claim_id="CLM-FATHER-CHASSIS-G6",
        subject_id=subject.subject_id,
        domain="software_platform",
        capability="industrial_qualification",
        claimed_level="C6",
        status="QUALIFIED" if data.get("final_industrial_pass") else "UNQUALIFIED",
    )

    observed_at = datetime.fromtimestamp(
        manifest_path.stat().st_mtime,
        tz=timezone.utc,
    ).isoformat()
    records: list[EvidenceRecord] = []
    for gate, gate_data in sorted(data.get("gates", {}).items()):
        artifact = str(gate_data.get("artifact", ""))
        artifact_path = manifest_path.parent / artifact
        artifact_hash = _file_sha256(artifact_path) if artifact_path.is_file() else ""
        records.append(EvidenceRecord(
            evidence_id=f"EVD-{gate.replace('.', '-')}",
            subject_id=subject.subject_id,
            claim_id=claim.claim_id,
            evidence_type="qualification_gate",
            artifact_ref=artifact,
            artifact_hash=artifact_hash,
            observed_at=observed_at,
            issuer="FATHER",
            metadata={
                "gate": gate,
                "status": str(gate_data.get("status", "UNKNOWN")),
            },
        ))

    return subject, claim, tuple(records)
