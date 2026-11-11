from __future__ import annotations

import os
from pathlib import Path

from father.adapters.models import OpenAICompatibleModel
from father.adapters.postgres import PostgreSQLStateStore
from father.adapters.redis_streams import RedisStreamsEventBus
from father.bootstrap import build_runtime
from father.core.audit import SQLiteAuditStore


def build_runtime_from_env():
    data_dir = Path(os.getenv("FATHER_DATA_DIR", "./data"))
    config_path = os.getenv("FATHER_CONFIG", "config/chassis.json")

    state = None
    if os.getenv("FATHER_STATE_BACKEND", "sqlite").lower() == "postgres":
        dsn = os.environ["FATHER_POSTGRES_DSN"]
        state = PostgreSQLStateStore(dsn)
        state.initialize()

    event_bus = None
    if os.getenv("FATHER_EVENT_BUS", "memory").lower() == "redis":
        event_bus = RedisStreamsEventBus(os.environ["FATHER_REDIS_URL"])

    model = None
    model_url = os.getenv("FATHER_MODEL_BASE_URL", "").strip()
    model_name = os.getenv("FATHER_MODEL_NAME", "").strip()
    if model_url and model_name:
        model = OpenAICompatibleModel(
            model_url,
            model_name,
            os.getenv("FATHER_MODEL_API_KEY", ""),
        )

    audit = SQLiteAuditStore(data_dir / "audit.db")
    return build_runtime(
        config_path=config_path,
        data_dir=data_dir,
        state=state,
        event_bus=event_bus,
        primary_model=model,
        audit=audit,
    )
