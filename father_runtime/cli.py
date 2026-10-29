from __future__ import annotations

import argparse
import json

from .adapters import ChatCompletionsHTTPAdapter, GigaChatRESTAdapter, ReferenceStage000Adapter
from .generator import create_factory
from .inventory import inventory
from .preflight import model_preflight
from .runner import StageRunner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='father-factory')
    sub = p.add_subparsers(dest='command', required=True)

    create = sub.add_parser('create')
    create.add_argument('--profile', required=True)
    create.add_argument('--output-root', default='generated_factories')

    run = sub.add_parser('run-stage')
    run.add_argument('--stage', required=True)
    run.add_argument('--input', required=True)
    run.add_argument('--adapter', choices=['reference', 'local-http', 'gigachat'], default='reference')
    run.add_argument('--endpoint', default='http://127.0.0.1:11434/v1/chat/completions')
    run.add_argument('--model', default='local-model')
    run.add_argument('--run-type', default='REFERENCE')
    run.add_argument('--evidence-dir', default='.father/runs')

    sub.add_parser('inventory-models')
    sub.add_parser('model-preflight')
    return p


def main() -> int:
    args = build_parser().parse_args()

    if args.command == 'create':
        result = create_factory(args.profile, output_root=args.output_root)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        return 0

    if args.command == 'model-preflight':
        print(json.dumps(model_preflight(), ensure_ascii=False, indent=2))
        return 0

    if args.command == 'inventory-models':
        print(json.dumps(inventory(), ensure_ascii=False, indent=2))
        return 0

    if args.command == 'run-stage':
        if args.adapter == 'reference':
            adapter = ReferenceStage000Adapter()
        elif args.adapter == 'gigachat':
            adapter = GigaChatRESTAdapter(model_id=args.model)
        else:
            adapter = ChatCompletionsHTTPAdapter(args.endpoint, args.model)

        record = StageRunner(evidence_dir=args.evidence_dir).run(
            stage_path=args.stage,
            input_path=args.input,
            adapter=adapter,
            run_type=args.run_type,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record['result']['status'] == 'PASS' else 2
    return 1
