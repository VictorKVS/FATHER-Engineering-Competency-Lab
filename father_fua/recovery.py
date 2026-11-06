from __future__ import annotations


NON_RETRYABLE = (PermissionError, ValueError)


def retry(operation, *, attempts: int, retryable_exceptions: tuple[type[BaseException], ...] = (Exception,)):
    if attempts <= 0:
        raise ValueError("attempts must be positive")

    last = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except NON_RETRYABLE:
            raise
        except retryable_exceptions as exc:
            last = exc
            if attempt == attempts:
                raise

    raise RuntimeError("retry exhausted without result") from last
