from __future__ import annotations

import argparse
import json

from .adapters import OpenAICompatibleHTTPAdapter, ReferenceStage000Adapter
from .runner import StageRunner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="father-factory")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run-stage")
    run.add_argument("--stage", required=True)
    run.add_argument("--input", required=True)
    run.add_argument("--adapter", choices=["reference", "openai-http"], default="reference")
    run.add_argument("--endpoint", default="http://127.0.0.1:11434/v1/chat/completions")
    run.add_argument("--model", default="local-model")
    run.add_argument("--run-type", default="REFERENCE")
    run.add_argument("--evidence-dir", default=".father/runs")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run-stage":
        if args.adapter == "reference":
            adapter = ReferenceStage000Adapter()
        else:
            adapter = OpenAICompatibleHTTPAdapter(args.endpoint, args.model)

        record = StageRunner(evidence_dir=args.evidence_dir).run(
            stage_path=args.stage,
            input_path=args.input,
            adapter=adapter,
            run_type=args.run_type,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record["result"]["status"] == "PASS" else 2
    return 1
