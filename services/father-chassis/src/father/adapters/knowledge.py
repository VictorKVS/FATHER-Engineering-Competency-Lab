from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from father.core.contracts import TraceContext

_TOKEN = re.compile(r"[\w-]+", re.UNICODE)

class SQLiteKnowledgeRag:
    """Dependency-free persistent knowledge store with deterministic lexical ranking."""
    name = "sqlite-knowledge-rag-v1"
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, source TEXT NOT NULL, text TEXT NOT NULL)")

    def health(self) -> bool:
        try:
            with sqlite3.connect(self.path) as db: db.execute("SELECT 1")
            return True
        except sqlite3.Error: return False

    def ingest(self, source: str, text: str, *, chunk_chars: int = 700) -> int:
        text = text.strip()
        if not text: return 0
        chunks = [text[i:i+chunk_chars].strip() for i in range(0, len(text), chunk_chars) if text[i:i+chunk_chars].strip()]
        with sqlite3.connect(self.path) as db:
            db.executemany("INSERT INTO chunks(source,text) VALUES(?,?)", [(source,c) for c in chunks])
        return len(chunks)

    def retrieve(self, query: str, trace: TraceContext) -> list[dict]:
        del trace
        terms = {t.lower() for t in _TOKEN.findall(query) if len(t) > 2}
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT id,source,text FROM chunks").fetchall()
        ranked = []
        for cid, source, text in rows:
            hay = text.lower()
            hits = sum(hay.count(t) for t in terms)
            if hits:
                ranked.append((hits, cid, source, text))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        return [{"chunk_id":cid,"source":source,"text":text,"score":float(score)} for score,cid,source,text in ranked[:5]]
