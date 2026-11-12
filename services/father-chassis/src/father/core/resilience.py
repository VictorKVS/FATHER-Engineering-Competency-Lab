from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import TypeVar

T = TypeVar("T")


class OperationTimeout(TimeoutError):
    pass


def call_with_retry_timeout(
    fn: Callable[[], T], *, attempts: int, timeout_ms: int
) -> T:
    last_exc: BaseException | None = None
    for _ in range(max(1, attempts)):
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(fn)
        try:
            value = future.result(timeout=timeout_ms / 1000)
            executor.shutdown(wait=True, cancel_futures=True)
            return value
        except FutureTimeoutError as exc:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
            last_exc = OperationTimeout(f"operation timed out after {timeout_ms} ms")
        except BaseException as exc:
            executor.shutdown(wait=True, cancel_futures=True)
            last_exc = exc
    if last_exc is None:
        raise RuntimeError("retry loop finished without a result or captured exception")
    raise last_exc
