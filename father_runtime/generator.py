from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil

import yaml

from .config import load_yaml


PROFILE_MAP = {
    'OSINT_FACTORY': 'factory/templates/examples/OSINT_FACTORY_PROFILE.yaml',
}


@dataclass
class FactoryCreateResult:
    factory_id: str
    output_dir: str
    profile_source: str
    manifest_path: str
    created_files: list[str]


def _safe_name(value: str) -> str:
    return ''.join(ch if ch.isalnum() or ch in '-_' else '-' for ch in value).strip('-') or 'factory-instance'


def create_factory(profile_name: str, repo_root: str | Path = '.', output_root: str | Path = 'generated_factories') -> FactoryCreateResult:
    root = Path(repo_root)
    if profile_name not in PROFILE_MAP:
        raise ValueError(f"Unknown profile {profile_name}. Available: {', '.join(sorted(PROFILE_MAP))}")

    profile_ref = PROFILE_MAP[profile_name]
    profile_path = root / profile_ref
    profile_doc = load_yaml(profile_path)
    profile = profile_doc.get('factory_profile', profile_doc)

    identity = profile.get('identity', {})
    factory_id = identity.get('factory_id') or profile_name
    instance_dir = Path(output_root) / _safe_name(factory_id)
    if instance_dir.exists():
        raise FileExistsError(f'{instance_dir} already exists')

    (instance_dir / 'config').mkdir(parents=True)
    (instance_dir / 'evidence').mkdir(parents=True)
    (instance_dir / 'runs').mkdir(parents=True)

    copied_profile = instance_dir / 'config' / 'factory_profile.yaml'
    shutil.copy2(profile_path, copied_profile)
    created_files = [str(copied_profile)]

    agent_set_ref = profile.get('intelligence', {}).get('agent_set_ref')
    if agent_set_ref:
        src = root / agent_set_ref
        if src.exists():
            dst = instance_dir / 'config' / 'agent_set.yaml'
            shutil.copy2(src, dst)
            created_files.append(str(dst))

    manifest = {
        'factory_instance': {
            'schema': 'father.factory_instance.v1',
            'instance_id': factory_id,
            'blueprint_version': '0.1.0',
            'profile_ref': str(copied_profile),
            'resolved': {
                'chassis': profile.get('product_model', {}).get('chassis_ref'),
                'blocks': profile.get('product_model', {}).get('required_blocks', []),
                'agents': [],
                'models': [],
                'tools': [],
                'stores': [],
                'policies': [],
                'gates': [],
                'ui_modules': [profile.get('ui', {}).get('ui_profile_ref')] if profile.get('ui') else [],
            },
            'replaceable_slots': {
                'models': ['MODEL_SLOT'],
                'agents': [],
                'tools': [],
                'stores': [],
                'ui': [],
            },
            'hard_constraints': [
                'no_stage_pass_without_evidence',
                'no_uncontrolled_tool_access',
                'no_untracked_production_code',
                'no_release_without_trust_verification',
            ],
            'state': {'current_stage': '000', 'status': 'DRAFT'},
            'provenance': {
                'created_from_blueprint': 'factory/templates/FACTORY_BLUEPRINT_CANON.md',
                'source_profile': profile_ref,
                'created_at': datetime.now(timezone.utc).isoformat(),
            },
        }
    }

    manifest_path = instance_dir / 'factory_instance.yaml'
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding='utf-8')
    created_files.append(str(manifest_path))

    readme = instance_dir / 'README.md'
    readme.write_text(
        '# ' + identity.get('name', factory_id) + '\n\n'
        + 'Generated from FATHER Factory Blueprint.\n\n'
        + '- Factory ID: ' + factory_id + '\n'
        + '- Class: ' + identity.get('class', 'UNKNOWN') + '\n'
        + '- Source profile: ' + profile_ref + '\n'
        + '- Initial stage: 000\n'
        + '- Status: DRAFT\n',
        encoding='utf-8',
    )
    created_files.append(str(readme))

    return FactoryCreateResult(
        factory_id=factory_id,
        output_dir=str(instance_dir),
        profile_source=profile_ref,
        manifest_path=str(manifest_path),
        created_files=created_files,
    )


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--profile', required=True)
    p.add_argument('--output-root', default='generated_factories')
    args = p.parse_args()
    result = create_factory(args.profile, output_root=args.output_root)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
