from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import time
import uuid

from .adapters import ModelAdapter
from .config import load_yaml, sha256_json, sha256_text
from .context import ContextBuilder


class StageRunner:
    def __init__(self, repo_root: str | Path = ".", evidence_dir: str | Path = ".father/runs") -> None:
        self.repo_root = Path(repo_root)
        self.evidence_dir = Path(evidence_dir)

    @staticmethod
    def _required_output_fields(stage: dict[str, Any]) -> list[str]:
        spec = stage.get("stage", stage)
        return list(spec.get("output", {}).get("required", []))

    def _validate_output(self, stage: dict[str, Any], output: dict[str, Any]) -> tuple[bool, list[str]]:
        missing = [k for k in self._required_output_fields(stage) if k not in output]
        return (not missing, missing)

    def run(
        self,
        stage_path: str | Path,
        input_path: str | Path,
        adapter: ModelAdapter,
        run_type: str,
    ) -> dict[str, Any]:
        stage = load_yaml(self.repo_root / stage_path)
        input_payload = load_yaml(self.repo_root / input_path)
        context = ContextBuilder(self.repo_root).build(stage, input_payload)

        run_id = str(uuid.uuid4())
        started = datetime.now(timezone.utc)
        t0 = time.perf_counter()
        result = adapter.run(context)
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)
        completed = datetime.now(timezone.utc)

        schema_valid, missing = self._validate_output(stage, result.parsed_output)
        spec = stage.get("stage", stage)

        record = {
            "run_id": run_id,
            "product_id": "FATHER-PLATFORM",
            "stage_id": str(spec.get("id", "")),
            "run_type": run_type,
            "model_id": result.model_id,
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "versions": {
                "stage_path": str(stage_path),
                "context_hash": sha256_json(context),
                **context.get("hashes", {}),
            },
            "metrics": {
                "latency_ms": latency_ms,
                "schema_valid": schema_valid,
                "missing_required_fields": missing,
            },
            "result": {
                "status": "PASS" if schema_valid else "FAIL",
                "parsed_output": result.parsed_output,
                "raw_output_sha256": sha256_text(result.raw_output),
                "parsed_output_sha256": sha256_json(result.parsed_output),
            },
        }

        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        out = self.evidence_dir / f"{spec.get('id','unknown')}-{run_type.lower()}-{run_id}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        record["evidence_path"] = str(out)
        return record
