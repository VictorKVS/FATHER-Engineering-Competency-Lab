from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import subprocess

import yaml

from .event_log import FactoryEventLogger


class DemoAutopilot:
    def __init__(self) -> None:
        self.events = FactoryEventLogger()

    @staticmethod
    def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, capture_output=True, shell=False)

    @staticmethod
    def _lane(number: int) -> str:
        if number <= 9: return "INTENT_AND_FACTORY_FOUNDATION"
        if number <= 19: return "CORE_PLATFORM"
        if number <= 29: return "MODEL_TOOL_MEMORY_FABRIC"
        if number <= 39: return "AGENT_AND_WORKFLOW_RUNTIME"
        if number <= 49: return "DATA_KNOWLEDGE_EVIDENCE"
        if number <= 59: return "SECURITY_AND_ASSURANCE"
        if number <= 69: return "TEST_EVAL_OBSERVABILITY"
        if number <= 79: return "RUNTIME_AND_DEVSECOPS"
        if number <= 89: return "UI_AND_ENGINEERING_WORKSPACE"
        if number <= 99: return "RELEASE_AND_POLYGON"
        return "PRODUCTION_PROVEN"

    @staticmethod
    def _name(number: int) -> str:
        names={
            0:"IDEA_INTAKE",1:"PROJECT_INITIALIZATION",2:"PRODUCT_INTENT",
            3:"BUSINESS_REQUIREMENTS",4:"BUSINESS_PROCESS",5:"SYSTEM_AND_DOMAIN",
            6:"SECURITY_AND_COMPLIANCE",7:"PROFESSION_AND_COMPETENCY",
            8:"KNOWLEDGE_REQUIREMENTS",9:"RESEARCH_PLAN",100:"PRODUCTION_PROVEN",
        }
        return names.get(number, f"MINIMAL_{DemoAutopilot._lane(number)}_{number:03d}")

    def run(self, *, root: str | Path, session_id: str, project_id: str, push: bool = True) -> dict[str, Any]:
        root=Path(root)
        if not (root/"project.yaml").exists():
            raise FileNotFoundError(f"project.yaml not found in {root}")
        stages_dir=root/"stages"
        if len(list(stages_dir.glob("*.yaml"))) != 101:
            raise RuntimeError("Demo autopilot requires exactly 101 stage files")

        run_id=f"DEMO-{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}"
        started=datetime.now(timezone.utc).isoformat()
        results=[]

        self.events.emit(
            session_id=session_id, stage_id="STAGE-000", source="RUNTIME",
            event_type="EXECUTION_START", action="demo_autopilot_000_100",
            status="STARTED", project_id=project_id,
            details={"root":str(root),"run_id":run_id},
        )

        for number in range(101):
            sid=f"{number:03d}"
            stage_id=f"STAGE-{sid}"
            stage_path=stages_dir/f"{sid}.yaml"
            artifact_dir=root/"artifacts"/f"stage_{sid}"
            evidence_dir=root/"evidence"/f"stage_{sid}"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            evidence_dir.mkdir(parents=True, exist_ok=True)
            now=datetime.now(timezone.utc).isoformat()

            artifact={
                "schema":"NEXUS_DEMO_MINIMAL_ARTIFACT_V1",
                "run_id":run_id,
                "stage_id":stage_id,
                "stage_name":self._name(number),
                "lane":self._lane(number),
                "mode":"DEMO_AUTOPILOT",
                "implementation":"MINIMAL_IMPLEMENTATION",
                "summary":f"Minimal working artifact for {stage_id}.",
                "status":"PASS",
            }
            artifact_path=artifact_dir/"minimal_artifact.json"
            artifact_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2),encoding="utf-8")

            evidence={
                "schema":"NEXUS_DEMO_EVIDENCE_V1",
                "evidence_class":"DEMO_ONLY",
                "run_id":run_id,
                "stage_id":stage_id,
                "input_snapshot":{"previous_stage":"NONE" if number==0 else f"STAGE-{number-1:03d}","mode":"DEMO_AUTOPILOT"},
                "input_test_result":{"status":"PASS"},
                "specialist":{"mode":"MINIMAL_IMPLEMENTATION","role":"DEMO_AUTOPILOT"},
                "produced_artifacts":[str(artifact_path.relative_to(root)).replace("\\","/")],
                "artifact_test_result":{"status":"PASS"},
                "human_gate":{"decision":"DEMO_AUTO_APPROVED","production_valid":False},
                "timestamps":{"started":now,"completed":now},
            }
            evidence_path=evidence_dir/"demo_evidence.json"
            evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

            stage={
                "stage_id":stage_id,
                "number":number,
                "stable_number":sid,
                "name":self._name(number),
                "lane":self._lane(number),
                "state":"APPROVED",
                "applicability":"APPLICABLE",
                "gate":"DEMO_AUTO_APPROVED",
                "contract":"FACTORY_STAGE_CONTRACT_V1",
                "demo_mode":True,
                "production_valid":False,
                "input_test":{"status":"PASS"},
                "specialist_work":{"status":"PASS","mode":"MINIMAL_IMPLEMENTATION"},
                "artifact_test":{"status":"PASS"},
                "evidence":[str(evidence_path.relative_to(root)).replace("\\","/")],
                "human_gate":{"decision":"DEMO_AUTO_APPROVED"},
                "run_id":run_id,
            }
            stage_path.write_text(yaml.safe_dump(stage,allow_unicode=True,sort_keys=False),encoding="utf-8")

            self.events.emit(
                session_id=session_id, stage_id=stage_id, source="RUNTIME",
                event_type="EXECUTION_STEP", action="demo_stage_complete",
                status="PASS", project_id=project_id,
                details={"run_id":run_id,"number":number,"artifact":str(artifact_path),"evidence":str(evidence_path)},
            )
            results.append({"stage_id":stage_id,"status":"PASS"})

        project=yaml.safe_load((root/"project.yaml").read_text(encoding="utf-8"))
        project["current_stage"]="100"
        project["state"]="DEMO_PRODUCTION_PROVEN"
        project["demo_autopilot"]={"run_id":run_id,"status":"PASS","completed_stages":101,"production_valid":False}
        (root/"project.yaml").write_text(yaml.safe_dump(project,allow_unicode=True,sort_keys=False),encoding="utf-8")

        manifest={
            "schema":"NEXUS_DEMO_AUTOPILOT_MANIFEST_V1",
            "run_id":run_id,
            "project_id":project_id,
            "started_at":started,
            "completed_at":datetime.now(timezone.utc).isoformat(),
            "completed_stages":101,
            "passed_stages":101,
            "failed_stages":0,
            "final_stage":"STAGE-100",
            "final_state":"DEMO_PRODUCTION_PROVEN",
            "production_valid":False,
            "results":results,
        }
        final_dir=root/"evidence"/"demo_autopilot"
        final_dir.mkdir(parents=True,exist_ok=True)
        manifest_path=final_dir/f"{run_id}.json"
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

        git_result={"commit":None,"push":None}
        if (root/".git").exists():
            self._run(["git","add","."],cwd=root)
            commit=self._run(["git","commit","-m",f"demo autopilot: complete 000-100 {run_id}"],cwd=root)
            git_result["commit"]={"returncode":commit.returncode,"stdout":commit.stdout.strip(),"stderr":commit.stderr.strip()}
            if push and commit.returncode==0:
                pushed=self._run(["git","push"],cwd=root)
                git_result["push"]={"returncode":pushed.returncode,"stdout":pushed.stdout.strip(),"stderr":pushed.stderr.strip()}

        self.events.emit(
            session_id=session_id, stage_id="STAGE-100", source="TEST",
            event_type="TEST_RESULT", action="demo_autopilot_000_100",
            status="PASS", project_id=project_id,
            details={"run_id":run_id,"completed_stages":101,"manifest":str(manifest_path),"git":git_result},
        )
        return {"status":"PASS","run_id":run_id,"completed_stages":101,"manifest":str(manifest_path),"git":git_result}
