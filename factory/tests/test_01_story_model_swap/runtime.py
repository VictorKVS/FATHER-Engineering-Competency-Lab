from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import subprocess

from agents.alina.profiles.literary.automatic_eval import evaluate_story_record
from agents.alina.profiles.literary.benchmark.runtime import LiteraryBenchmark
from agents.alina.profiles.literary.runtime import AlinaLiteraryRuntime
from father_runtime.model_swap import ModelSwapRouter


class StoryModelSwapTest:
    def __init__(
        self,
        repo_root: str | Path = ".",
        output_root: str | Path = "benchmark_results/test_01_story_model_swap",
        port: int = 8080,
        pass_threshold: int = 80,
    ) -> None:
        self.root = Path(repo_root)
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.port = port
        self.pass_threshold = pass_threshold
        self.benchmark = LiteraryBenchmark(repo_root=self.root, output_root=self.output_root / "_server_logs")

    def _run_id(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def run_failover(
        self,
        story_text: str,
        target_length: int = 500,
        constraints: list[str] | None = None,
        publish: bool = False,
    ) -> tuple[Path, dict[str, Any]]:
        run_id = self._run_id()
        run_dir = self.output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        evidence_dir = run_dir / "per_model_evidence"
        runtime = AlinaLiteraryRuntime(repo_root=self.root, evidence_dir=evidence_dir)
        router = ModelSwapRouter(pass_threshold=self.pass_threshold)
        candidates = self.benchmark.eligible_models()
        launch_meta: dict[str, dict[str, Any]] = {}

        def execute(candidate: dict[str, Any]) -> dict[str, Any]:
            proc = log = None
            try:
                proc, log, log_path, alias, template = self.benchmark._start_server(
                    candidate,
                    port=self.port,
                )
                launch_meta[candidate["id"]] = {
                    "selected_template": template,
                    "server_log": str(log_path),
                    "api_alias": alias,
                }
                record = runtime.run(
                    story_text=story_text,
                    endpoint=f"http://127.0.0.1:{self.port}/v1/chat/completions",
                    model_id=alias,
                    target_length=target_length,
                    constraints=constraints or [],
                )
                record["catalog_model_id"] = candidate["id"]
                record["launch_template"] = template
                return record
            finally:
                if proc is not None and log is not None:
                    self.benchmark._stop_server(proc, log)

        selected, attempted = router.select(
            candidates=candidates,
            execute=execute,
            evaluate=evaluate_story_record,
        )
        leaderboard = router.leaderboard(attempted)

        result = {
            "test_id": "TEST-01-STORY-MODEL-SWAP",
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "mode": "FAILOVER",
            "fixed": {
                "agent": "AG-001",
                "profile": "ALINA_LITERARY",
                "capability": "STORY_CONTINUATION",
                "prompt_version": "0.2.0",
                "rag_version": "ALINA_LITERARY_RAG_V02",
                "kb_version": "0.2.0",
            },
            "variable": "model_id",
            "pass_threshold": self.pass_threshold,
            "candidate_count": len(candidates),
            "attempted_count": len(attempted),
            "selected_model": selected.model_id if selected else None,
            "gate": "PASS" if selected else "HOLD",
            "quality_gate": "PENDING_QUALITY_REVIEW",
            "attempts": [
                {
                    "model_id": r.model_id,
                    "status": r.status,
                    "automatic_score": r.score,
                    "latency_ms": r.latency_ms,
                    "hard_fails": list(r.hard_fails),
                    "launch": launch_meta.get(r.model_id, {}),
                    "evidence_path": r.payload.get("evidence_path"),
                    "error": r.payload.get("error"),
                }
                for r in attempted
            ],
        }

        leaderboard_payload = [
            {
                "rank": i + 1,
                "model_id": r.model_id,
                "status": r.status,
                "automatic_score": r.score,
                "latency_ms": r.latency_ms,
                "hard_fails": list(r.hard_fails),
            }
            for i, r in enumerate(leaderboard)
        ]

        (run_dir / "summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (run_dir / "leaderboard.json").write_text(
            json.dumps(leaderboard_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (run_dir / "selected_model.json").write_text(
            json.dumps(
                {
                    "selected_model": selected.model_id if selected else None,
                    "status": selected.status if selected else "HOLD",
                    "automatic_score": selected.score if selected else 0,
                    "latency_ms": selected.latency_ms if selected else 0,
                    "quality_gate": "PENDING_QUALITY_REVIEW",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self._write_review_bundle(run_dir, result, attempted)

        if publish:
            self.publish_git(run_dir)

        return run_dir, result

    @staticmethod
    def _write_review_bundle(run_dir: Path, result: dict[str, Any], attempted: list[Any]) -> None:
        lines = [
            "# TEST-01 — Story Model Swap",
            "",
            f"Run: {result['run_id']}",
            f"Gate: {result['gate']}",
            f"Selected model: {result['selected_model'] or 'NONE'}",
            f"Automatic threshold: {result['pass_threshold']}",
            "Quality gate: PENDING_QUALITY_REVIEW",
            "",
            "## Attempts",
            "",
        ]
        for item in attempted:
            lines += [
                f"### {item.model_id}",
                f"- status: {item.status}",
                f"- automatic score: {item.score}",
                f"- latency_ms: {item.latency_ms}",
                f"- hard fails: {', '.join(item.hard_fails) if item.hard_fails else 'none'}",
                "",
            ]
            output = (item.payload or {}).get("output") or {}
            continuation = output.get("continuation")
            if continuation:
                lines += ["#### Continuation", "", continuation, ""]
        (run_dir / "REVIEW_BUNDLE.md").write_text("\n".join(lines), encoding="utf-8")

    def publish_git(self, run_dir: Path) -> None:
        subprocess.run(["git", "add", str(run_dir)], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"test-01: publish story model swap {run_dir.name}"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "push"], cwd=self.root, check=True)
