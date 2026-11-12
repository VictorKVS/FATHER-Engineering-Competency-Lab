from __future__ import annotations

import json
from typing import Any


class MissingOptionalDependency(RuntimeError):
    pass


def _psycopg():
    try:
        import psycopg  # type: ignore
        return psycopg
    except ImportError as exc:
        raise MissingOptionalDependency("install father-chassis[postgres] (psycopg) for PostgreSQL adapters") from exc


class PostgreSQLStateStore:
    """Production state adapter. Connection is lazy so the base package stays dependency-free."""
    def __init__(self, dsn: str, table: str = "father_state") -> None:
        self.dsn = dsn
        self.table = table

    def initialize(self) -> None:
        psycopg = _psycopg()
        with psycopg.connect(self.dsn) as db:
            db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (namespace text, key text, value jsonb NOT NULL, PRIMARY KEY(namespace,key))")

    def health(self) -> bool:
        try:
            psycopg = _psycopg()
            with psycopg.connect(self.dsn) as db: db.execute("SELECT 1")
            return True
        except Exception:
            return False

    def set(self, namespace: str, key: str, value: Any) -> None:
        psycopg = _psycopg()
        with psycopg.connect(self.dsn) as db:
            db.execute(
                f"INSERT INTO {self.table}(namespace,key,value) VALUES(%s,%s,%s::jsonb) "
                f"ON CONFLICT(namespace,key) DO UPDATE SET value=excluded.value",
                (namespace, key, json.dumps(value)),
            )

    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        psycopg = _psycopg()
        with psycopg.connect(self.dsn) as db:
            row = db.execute(f"SELECT value FROM {self.table} WHERE namespace=%s AND key=%s", (namespace,key)).fetchone()
        return default if row is None else row[0]

    def snapshot(self, namespace: str) -> dict[str, Any]:
        psycopg = _psycopg()
        with psycopg.connect(self.dsn) as db:
            rows = db.execute(f"SELECT key,value FROM {self.table} WHERE namespace=%s", (namespace,)).fetchall()
        return {k:v for k,v in rows}


class PgVectorKnowledgeRag:
    """pgvector-ready adapter contract.

    Embedding is injected to keep model choice independent from storage. Requires a
    PostgreSQL database with the vector extension enabled.
    """
    name = "pgvector-knowledge-rag-v1"

    def __init__(self, dsn: str, embed, *, dimensions: int, table: str = "father_chunks") -> None:
        self.dsn, self.embed, self.dimensions, self.table = dsn, embed, dimensions, table

    def initialize(self) -> None:
        psycopg = _psycopg()
        with psycopg.connect(self.dsn) as db:
            db.execute("CREATE EXTENSION IF NOT EXISTS vector")
            db.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (id bigserial PRIMARY KEY, source text NOT NULL, text text NOT NULL, embedding vector({self.dimensions}))")

    def health(self) -> bool:
        try:
            psycopg = _psycopg()
            with psycopg.connect(self.dsn) as db: db.execute("SELECT 1")
            return True
        except Exception:
            return False

    def ingest(self, source: str, text: str, *, chunk_chars: int = 700) -> int:
        psycopg = _psycopg(); chunks=[text[i:i+chunk_chars].strip() for i in range(0,len(text),chunk_chars) if text[i:i+chunk_chars].strip()]
        with psycopg.connect(self.dsn) as db:
            for chunk in chunks:
                vector = self.embed(chunk)
                db.execute(f"INSERT INTO {self.table}(source,text,embedding) VALUES(%s,%s,%s)", (source,chunk,vector))
        return len(chunks)

    def retrieve(self, query, trace):
        del trace
        psycopg = _psycopg(); vector=self.embed(query)
        with psycopg.connect(self.dsn) as db:
            rows=db.execute(f"SELECT id,source,text,1-(embedding <=> %s) score FROM {self.table} ORDER BY embedding <=> %s LIMIT 5", (vector,vector)).fetchall()
        return [{"chunk_id":r[0],"source":r[1],"text":r[2],"score":float(r[3])} for r in rows]
