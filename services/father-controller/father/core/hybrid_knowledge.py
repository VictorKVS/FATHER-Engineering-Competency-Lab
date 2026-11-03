import json
import math
import re
import urllib.request
from pathlib import Path
from father.contracts.types import KnowledgeResult

class OllamaEmbeddingClient:
    def __init__(self,model="nomic-embed-text",base_url="http://127.0.0.1:11434"):
        self.model=model
        self.base_url=base_url.rstrip("/")

    def embed(self,texts):
        payload=json.dumps({"model":self.model,"input":texts},ensure_ascii=False).encode("utf-8")
        req=urllib.request.Request(
            self.base_url+"/api/embed",
            data=payload,
            headers={"Content-Type":"application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req,timeout=120) as r:
            data=json.loads(r.read().decode("utf-8"))
        return data["embeddings"]

class HybridFolderKnowledge:
    def __init__(self,folder,embedding_client,chunk_chars=1200,semantic_weight=0.7,lexical_weight=0.3):
        self.folder=Path(folder)
        self.embedding_client=embedding_client
        self.chunk_chars=chunk_chars
        self.semantic_weight=semantic_weight
        self.lexical_weight=lexical_weight
        self._index=None

    @staticmethod
    def _tokens(text):
        return set(re.findall(r"[A-Za-zА-Яа-яЁё0-9_-]{2,}",str(text).lower()))

    @staticmethod
    def _cosine(a,b):
        dot=sum(x*y for x,y in zip(a,b))
        na=math.sqrt(sum(x*x for x in a))
        nb=math.sqrt(sum(y*y for y in b))
        return dot/(na*nb) if na and nb else 0.0

    def _chunks(self):
        rows=[]
        files=list(self.folder.glob("**/*.md"))+list(self.folder.glob("**/*.txt"))
        for p in sorted(files):
            text=p.read_text(encoding="utf-8",errors="ignore")
            for i in range(0,len(text),self.chunk_chars):
                chunk=text[i:i+self.chunk_chars].strip()
                if chunk:
                    rows.append({
                        "source":str(p),
                        "chunk":i//self.chunk_chars,
                        "text":chunk
                    })
        return rows

    def build_index(self):
        rows=self._chunks()
        vectors=self.embedding_client.embed([x["text"] for x in rows]) if rows else []
        self._index=[]
        for item,vec in zip(rows,vectors):
            x=dict(item)
            x["embedding"]=vec
            self._index.append(x)
        return {
            "status":"ok",
            "documents":len({x["source"] for x in rows}),
            "chunks":len(rows),
            "embedding_model":self.embedding_client.model
        }

    def health(self):
        if self._index is None:
            self.build_index()
        return {
            "status":"ok" if self.folder.exists() and self._index else "error",
            "adapter":"hybrid-folder",
            "documents":len({x["source"] for x in self._index or []}),
            "chunks":len(self._index or []),
            "embedding_model":self.embedding_client.model,
            "semantic_weight":self.semantic_weight,
            "lexical_weight":self.lexical_weight
        }

    def search(self,query):
        if self._index is None:
            self.build_index()
        if not self._index:
            return KnowledgeResult(items=[])

        qvec=self.embedding_client.embed([str(query.text)])[0]
        qtokens=self._tokens(query.text)

        max_lex=max(
            [len(qtokens & self._tokens(x["text"])) for x in self._index] or [1]
        )
        max_lex=max(max_lex,1)

        scored=[]
        for item in self._index:
            semantic=self._cosine(qvec,item["embedding"])
            lexical=len(qtokens & self._tokens(item["text"]))/max_lex
            hybrid=self.semantic_weight*semantic+self.lexical_weight*lexical
            scored.append({
                "source":item["source"],
                "chunk":item["chunk"],
                "text":item["text"],
                "semantic_score":round(semantic,6),
                "lexical_score":round(lexical,6),
                "score":round(hybrid,6),
                "retrieval_mode":"hybrid-semantic-lexical",
                "embedding_model":self.embedding_client.model
            })

        scored.sort(key=lambda x:x["score"],reverse=True)
        return KnowledgeResult(items=scored[:query.top_k])
