from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
import urllib.request


def _run(args: list[str]) -> str | None:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=20, check=False)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _json_get(url: str, timeout: int = 3) -> dict | list | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
        return None


def detect_ollama() -> dict:
    rows=[]
    cli_found=bool(shutil.which('ollama'))
    if cli_found:
        out=_run(['ollama','list'])
        if out:
            for line in out.splitlines()[1:]:
                parts=line.split()
                if parts:
                    rows.append({'provider':'LOCAL_OLLAMA','model':parts[0],'source':'ollama list','raw':line})

    api=_json_get('http://127.0.0.1:11434/api/tags')
    if isinstance(api, dict):
        for item in api.get('models', []):
            name=item.get('name') or item.get('model')
            if name and not any(x.get('model')==name for x in rows):
                rows.append({'provider':'LOCAL_OLLAMA','model':name,'source':'ollama api','details':item})

    return {'cli_found':cli_found,'api_reachable':isinstance(api,dict),'models':rows}


def _windows_model_roots() -> list[Path]:
    roots=[]
    home=Path.home()
    candidates=[
        home / '.ollama' / 'models',
        home / '.cache' / 'lm-studio' / 'models',
        home / '.lmstudio' / 'models',
        home / 'AppData' / 'Local' / 'LM Studio' / 'models',
        home / 'AppData' / 'Roaming' / 'LM Studio' / 'models',
        Path('C:/Users/Public/Documents/LM Studio/models'),
        Path('G:/models'),
        Path('G:/1/models'),
        Path('G:/LLM'),
        Path('G:/1/LLM'),
    ]
    for p in candidates:
        if p.exists():
            roots.append(p)
    return roots


def _configured_roots() -> list[Path]:
    roots=[]
    for env_name in ('FATHER_MODEL_DIR','FATHER_EXTRA_MODEL_DIR','OLLAMA_MODELS'):
        value=os.getenv(env_name)
        if value:
            p=Path(value)
            if p.exists():
                roots.append(p)
    for p in (Path('models'),Path('data/models')):
        if p.exists():
            roots.append(p)
    roots.extend(_windows_model_roots())
    dedup=[]
    seen=set()
    for p in roots:
        try:
            key=str(p.resolve()).lower()
        except OSError:
            key=str(p).lower()
        if key not in seen:
            seen.add(key); dedup.append(p)
    return dedup


def detect_gguf() -> dict:
    roots=_configured_roots()
    rows=[]
    seen=set()
    for root in roots:
        try:
            iterator=root.rglob('*.gguf')
            for p in iterator:
                key=str(p.resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                rows.append({'provider':'LOCAL_GGUF','model':p.name,'path':str(p),'size_bytes':p.stat().st_size})
        except (OSError, PermissionError):
            continue
    return {'roots_scanned':[str(x) for x in roots],'models':rows}


def detect_lm_studio() -> dict:
    endpoints=[
        'http://127.0.0.1:1234/v1/models',
        'http://localhost:1234/v1/models',
    ]
    for url in endpoints:
        data=_json_get(url)
        if isinstance(data, dict):
            rows=[]
            for item in data.get('data', []):
                if isinstance(item, dict) and item.get('id'):
                    rows.append({'provider':'LOCAL_LM_STUDIO','model':item['id'],'details':item})
            return {'api_reachable':True,'endpoint':url,'models':rows}
    return {'api_reachable':False,'endpoint':None,'models':[]}


def inventory() -> dict:
    return {
        'ollama': detect_ollama(),
        'lm_studio': detect_lm_studio(),
        'gguf': detect_gguf(),
        'environment': {
            'FATHER_MODEL_DIR': os.getenv('FATHER_MODEL_DIR'),
            'FATHER_EXTRA_MODEL_DIR': os.getenv('FATHER_EXTRA_MODEL_DIR'),
            'OLLAMA_MODELS': os.getenv('OLLAMA_MODELS'),
        },
    }


def main() -> int:
    print(json.dumps(inventory(), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
