from __future__ import annotations


def retry(operation, *, attempts: int):
    last = None
    for _ in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last = exc
    raise last
