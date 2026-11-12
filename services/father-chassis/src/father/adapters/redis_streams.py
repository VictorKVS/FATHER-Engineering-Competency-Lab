from __future__ import annotations
import json
from father.core.contracts import Event


class RedisStreamsEventBus:
    def __init__(self, url: str, stream: str = "father-events") -> None:
        try:
            import redis  # type: ignore
        except ImportError as exc:
            raise RuntimeError("install redis package for RedisStreamsEventBus") from exc
        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.stream = stream

    def health(self) -> bool:
        try: return bool(self.client.ping())
        except Exception: return False

    def publish(self, event: Event) -> None:
        self.client.xadd(self.stream, {"type":event.type,"trace_id":event.trace_id,"ts":event.ts,"payload":json.dumps(event.payload)})

    def subscribe(self, event_type: str, handler) -> None:
        raise NotImplementedError("consumer groups run outside the synchronous chassis process")

    def by_trace(self, trace_id: str) -> list[Event]:
        raise NotImplementedError("query events from the audit store or an indexed event sink")
