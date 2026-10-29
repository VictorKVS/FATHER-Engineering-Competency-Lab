from __future__ import annotations

import argparse
import json
import yaml
from pathlib import Path

from .adapters import ChatCompletionsHTTPAdapter, GigaChatRESTAdapter, ReferenceStage000Adapter
from .generator import create_factory
from .inventory import inventory
from .preflight import model_preflight
from .runner import StageRunner
from agents.story_continuation.runtime import StoryAgent
from agents.alina.profiles.literary.runtime import AlinaLiteraryRuntime
from agents.alina.profiles.literary.benchmark.runtime import LiteraryBenchmark
from factory.tests.test_01_story_model_swap.runtime import StoryModelSwapTest


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
    sub.add_parser('model-catalog')
    sub.add_parser('model-preflight')

    t1 = sub.add_parser('test-01-story-model-swap')
    t1.add_argument('--file', default='factory/tests/test_01_story_model_swap/STORY_INPUT.txt')
    t1.add_argument('--target-length', type=int, default=500)
    t1.add_argument('--output-root', default='benchmark_results/test_01_story_model_swap')
    t1.add_argument('--publish', action='store_true')

    bench = sub.add_parser('literary-benchmark')
    bench.add_argument('--output-root', default='benchmark_results/alina_literary')
    bench.add_argument('--publish', action='store_true')

    alina = sub.add_parser('alina-literary-continue')
    alina.add_argument('--file', required=True)
    alina.add_argument('--endpoint', default='http://127.0.0.1:8080/v1/chat/completions')
    alina.add_argument('--model', required=True)
    alina.add_argument('--target-length', type=int, default=500)
    alina.add_argument('--evidence-dir', default='.father/alina_literary_runs')

    story = sub.add_parser('story-continue')
    story.add_argument('--file', required=True)
    story.add_argument('--endpoint', default='http://127.0.0.1:8080/v1/chat/completions')
    story.add_argument('--model', required=True)
    story.add_argument('--target-length', type=int, default=500)
    story.add_argument('--evidence-dir', default='.father/story_runs')
    return p


def main() -> int:
    args = build_parser().parse_args()

    if args.command == 'create':
        result = create_factory(args.profile, output_root=args.output_root)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        return 0

    if args.command == 'test-01-story-model-swap':
        story_text = Path(args.file).read_text(encoding='utf-8')
        run_dir, result = StoryModelSwapTest(output_root=args.output_root).run_failover(
            story_text=story_text,
            target_length=args.target_length,
            publish=args.publish,
        )
        print(json.dumps({
            'run_dir': str(run_dir),
            'gate': result['gate'],
            'selected_model': result['selected_model'],
            'attempted_count': result['attempted_count'],
            'quality_gate': result['quality_gate'],
            'published': bool(args.publish),
        }, ensure_ascii=False, indent=2))
        return 0 if result['gate'] == 'PASS' else 2

    if args.command == 'literary-benchmark':
        bench = LiteraryBenchmark(output_root=args.output_root)
        run_dir, manifest = bench.run()
        if args.publish:
            bench.publish_git(run_dir)
        print(json.dumps({'run_dir': str(run_dir), 'automatic_model_count': manifest['automatic_model_count'], 'published': bool(args.publish)}, ensure_ascii=False, indent=2))
        return 0

    if args.command == 'alina-literary-continue':
        story_text = Path(args.file).read_text(encoding='utf-8')
        record = AlinaLiteraryRuntime(evidence_dir=args.evidence_dir).run(
            story_text=story_text,
            endpoint=args.endpoint,
            model_id=args.model,
            target_length=args.target_length,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record['contract_valid'] else 2

    if args.command == 'story-continue':
        story_text = Path(args.file).read_text(encoding='utf-8')
        record = StoryAgent(evidence_dir=args.evidence_dir).run(
            story_text=story_text,
            endpoint=args.endpoint,
            model_id=args.model,
            target_length=args.target_length,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0 if record['contract_valid'] else 2

    if args.command == 'model-preflight':
        print(json.dumps(model_preflight(), ensure_ascii=False, indent=2))
        return 0

    if args.command == 'model-catalog':
        catalog_path = Path('factory/model_fabric/LOCAL_MODEL_CATALOG.yaml')
        catalog = yaml.safe_load(catalog_path.read_text(encoding='utf-8'))['catalog']
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
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
