from __future__ import annotations

from hashlib import sha256
import re
import sqlite3
from pathlib import Path
from father.core.contracts import TraceContext

_TOKEN = re.compile(r"[\w-]+", re.UNICODE)


class SQLiteKnowledgeRag:
    """Persistent deterministic lexical RAG with idempotent evidence ingestion."""

    name = "sqlite-knowledge-rag-v1"

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS chunks ("
                "id INTEGER PRIMARY KEY, "
                "source TEXT NOT NULL, "
                "text TEXT NOT NULL, "
                "content_hash TEXT)"
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(chunks)").fetchall()}
            if "content_hash" not in columns:
                db.execute("ALTER TABLE chunks ADD COLUMN content_hash TEXT")

            rows = db.execute(
                "SELECT id, source, text FROM chunks WHERE content_hash IS NULL OR content_hash = ''"
            ).fetchall()
            for cid, source, text in rows:
                digest = sha256(text.encode("utf-8")).hexdigest()
                db.execute(
                    "UPDATE chunks SET content_hash=? WHERE id=?",
                    (digest, cid),
                )

            db.execute(
                "DELETE FROM chunks WHERE id NOT IN ("
                "SELECT MIN(id) FROM chunks GROUP BY source, content_hash)"
            )
            db.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_chunks_source_hash "
                "ON chunks(source, content_hash)"
            )

    def health(self) -> bool:
        try:
            with sqlite3.connect(self.path) as db:
                db.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def ingest(self, source: str, text: str, *, chunk_chars: int = 700) -> int:
        text = text.strip()
        if not text:
            return 0
        chunks = [
            text[i:i + chunk_chars].strip()
            for i in range(0, len(text), chunk_chars)
            if text[i:i + chunk_chars].strip()
        ]
        inserted = 0
        with sqlite3.connect(self.path) as db:
            for chunk in chunks:
                digest = sha256(chunk.encode("utf-8")).hexdigest()
                cursor = db.execute(
                    "INSERT OR IGNORE INTO chunks(source,text,content_hash) VALUES(?,?,?)",
                    (source, chunk, digest),
                )
                inserted += max(cursor.rowcount, 0)
        return inserted

    def retrieve(self, query: str, trace: TraceContext) -> list[dict]:
        del trace
        terms = {t.lower() for t in _TOKEN.findall(query) if len(t) > 2}
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id,source,text,content_hash FROM chunks"
            ).fetchall()

        ranked = []
        for cid, source, text, content_hash in rows:
            hay = text.lower()
            hits = sum(hay.count(t) for t in terms)
            if hits:
                ranked.append((hits, cid, source, text, content_hash))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        return [
            {
                "chunk_id": cid,
                "source": source,
                "text": text,
                "score": float(score),
                "content_hash": content_hash,
            }
            for score, cid, source, text, content_hash in ranked[:5]
        ]
