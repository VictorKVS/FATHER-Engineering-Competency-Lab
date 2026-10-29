from __future__ import annotations

import json
import shutil
import urllib.request


def _reachable(url: str, timeout: int = 3) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def model_preflight() -> dict:
    return {
        'llama_server': {
            'found': bool(shutil.which('llama-server')),
            'path': shutil.which('llama-server'),
            'api_reachable': _reachable('http://127.0.0.1:8080/v1/models'),
        },
        'lm_studio': {
            'api_reachable': _reachable('http://127.0.0.1:1234/v1/models'),
        },
        'ollama': {
            'cli_found': bool(shutil.which('ollama')),
            'api_reachable': _reachable('http://127.0.0.1:11434/api/tags'),
        },
    }


def main() -> int:
    print(json.dumps(model_preflight(), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
