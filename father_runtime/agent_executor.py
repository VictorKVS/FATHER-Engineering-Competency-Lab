from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import uuid

import yaml

from .adapters import ModelAdapter
from .agent_construct import AgentConstruct


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _sha256_json(payload: Any) -> str:
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass
class AgentExecutionResult:
    run_id: str
    status: str
    model_id: str
    output: dict[str, Any]
    hard_fails: list[str]
    evidence_path: str


class AgentExecutor:
    def __init__(self, repo_root: str | Path=".") -> None:
        self.repo_root=Path(repo_root)

    def _validate_input(self, contract: dict[str, Any], payload: dict[str, Any]) -> list[str]:
        spec=contract.get("contract",contract)
        errors=[]
        for key in spec.get("required",[]):
            if key not in payload:
                errors.append(f"missing_input:{key}")
        return errors

    def _validate_output(self, contract: dict[str, Any], payload: dict[str, Any]) -> list[str]:
        spec=contract.get("contract",contract)
        errors=[]
        for key in spec.get("required",[]):
            if key not in payload:
                errors.append(f"missing_output:{key}")
        return errors

    def run(
        self,
        *,
        agent_path: str | Path,
        input_contract_path: str | Path,
        output_contract_path: str | Path,
        task_input: dict[str, Any],
        adapter: ModelAdapter,
        evidence_dir: str | Path=".father/agent-runs",
    ) -> AgentExecutionResult:
        agent_doc=_load_yaml(self.repo_root/agent_path)
        construct=AgentConstruct.from_dict(agent_doc)
        input_contract=_load_yaml(self.repo_root/input_contract_path)
        output_contract=_load_yaml(self.repo_root/output_contract_path)

        run_id=str(uuid.uuid4())
        started=datetime.now(timezone.utc).isoformat()
        hard_fails=self._validate_input(input_contract,task_input)
        if hard_fails:
            output={}
            model_id=getattr(adapter,"model_id","UNKNOWN")
            status="FAIL"
        else:
            context={
                "agent":construct.frozen_context(),
                "task_input":task_input,
                "security":{
                    "deny_by_default":True,
                    "tools_allowed":[],
                    "persistent_memory_write":False,
                },
            }
            result=adapter.run(context)
            output=result.parsed_output
            model_id=result.model_id
            hard_fails=self._validate_output(output_contract,output)
            status="PASS" if not hard_fails else "FAIL"

        completed=datetime.now(timezone.utc).isoformat()
        evidence={
            "schema":"FATHER_AGENT_EXECUTION_EVIDENCE_V1",
            "run_id":run_id,
            "agent_id":construct.agent_id,
            "model_id":model_id,
            "status":status,
            "hard_fails":hard_fails,
            "versions":construct.frozen_context(),
            "task_input_sha256":_sha256_json(task_input),
            "output_sha256":_sha256_json(output),
            "output":output,
            "security":{
                "deny_by_default":True,
                "tools_allowed":[],
                "persistent_memory_write":False,
            },
            "timestamps":{"started_at":started,"completed_at":completed},
        }
        out_dir=self.repo_root/Path(evidence_dir)
        out_dir.mkdir(parents=True,exist_ok=True)
        out=out_dir/f"{construct.agent_id}-{run_id}.json"
        out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
        return AgentExecutionResult(run_id,status,model_id,output,hard_fails,str(out))
