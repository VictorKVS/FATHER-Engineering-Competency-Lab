from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml


STANDARD_DIRS = [
    "canonical",
    "stages",
    "artifacts",
    "agents",
    "algorithms",
    "knowledge",
    "models",
    "tools",
    "tests",
    "evidence",
    "releases",
    ".factory",
]


class ProjectScaffoldGenerator:
    def __init__(self, stage_map_path: str | Path = "factory/project/PROJECT_STAGE_MAP.yaml") -> None:
        self.stage_map_path = Path(stage_map_path)

    def _stage_map(self) -> dict[str, Any]:
        return yaml.safe_load(self.stage_map_path.read_text(encoding="utf-8"))["project_stage_map"]

    def create(
        self,
        root: str | Path,
        *,
        project_id: str,
        public_name: str,
        code_name: str,
        approved: bool,
    ) -> Path:
        if not approved:
            raise PermissionError("Project scaffold creation requires explicit STAGE-001 approval")

        root = Path(root)
        root.mkdir(parents=True, exist_ok=False)

        for rel in STANDARD_DIRS:
            (root / rel).mkdir(parents=True, exist_ok=True)

        stage_map = self._stage_map()
        names = stage_map.get("canonical_named_stages", {})

        project = {
            "schema": "ENGINEERING_PROJECT_V1",
            "project_id": project_id,
            "public_name": public_name,
            "code_name": code_name,
            "version": "0.1.0",
            "state": "DRAFT",
            "stage_range": "000-100",
            "current_stage": "001",
            "factory_contract": "FACTORY_STAGE_CONTRACT_V1",
        }
        (root / "project.yaml").write_text(
            yaml.safe_dump(project, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        for number in range(101):
            sid = f"{number:03d}"
            stage = {
                "stage_id": f"STAGE-{sid}",
                "number": number,
                "stable_number": sid,
                "name": names.get(sid, f"RESERVED_STAGE_{sid}"),
                "lane": self._lane_for(number, stage_map["ranges"]),
                "state": "LOCKED",
                "applicability": "UNASSESSED",
                "gate": "LOCKED",
                "contract": "FACTORY_STAGE_CONTRACT_V1",
                "input_test": {"status": "NOT_RUN"},
                "artifact_test": {"status": "NOT_RUN"},
                "evidence": [],
                "human_gate": {"decision": None},
            }
            if number == 0:
                stage["state"] = "APPROVED"
                stage["gate"] = "APPROVED"
            elif number == 1:
                stage["state"] = "READY"
                stage["gate"] = "PENDING"

            (root / "stages" / f"{sid}.yaml").write_text(
                yaml.safe_dump(stage, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

        manifest = {
            "project_id": project_id,
            "created_stage_files": 101,
            "first_stage": "000",
            "last_stage": "100",
            "standard_directories": STANDARD_DIRS,
        }
        (root / ".factory" / "scaffold_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return root

    @staticmethod
    def _lane_for(number: int, ranges: list[dict[str, Any]]) -> str:
        for item in ranges:
            raw = str(item["range"])
            if "-" in raw:
                start, end = (int(x) for x in raw.split("-", 1))
            else:
                start = end = int(raw)
            if start <= number <= end:
                return item["lane"]
        raise ValueError(f"No lane for stage {number}")
