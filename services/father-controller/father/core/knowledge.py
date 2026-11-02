from pathlib import Path
import re
from father.contracts.types import KnowledgeResult

class NullKnowledge:
    def health(self):
        return {"status":"ok","adapter":"null","documents":0}
    def search(self,query):
        return KnowledgeResult(items=[])

class FolderKnowledge:
    """
    Bootstrap retrieval adapter.

    Strategy:
    1. lexical token-overlap ranking;
    2. if no lexical hit exists, return the first available chunks as an
       explicit fallback so a small Competency Pack is still injected into
       the agent context.

    The fallback is evidence-friendly: every returned item includes
    retrieval_mode = "lexical" or "fallback".
    """
    def __init__(self,folder,chunk_chars=1800,fallback_on_empty=True):
        self.folder=Path(folder)
        self.chunk_chars=chunk_chars
        self.fallback_on_empty=fallback_on_empty

    def health(self):
        fs=list(self.folder.glob("**/*.md"))+list(self.folder.glob("**/*.txt"))
        return {
            "status":"ok" if self.folder.exists() else "error",
            "adapter":"folder",
            "documents":len(fs),
            "fallback_on_empty":self.fallback_on_empty
        }

    @staticmethod
    def _tokens(text):
        return set(re.findall(r"[A-Za-zА-Яа-яЁё0-9_-]{2,}",str(text).lower()))

    def _chunks(self):
        for p in list(self.folder.glob("**/*.md"))+list(self.folder.glob("**/*.txt")):
            text=p.read_text(encoding="utf-8",errors="ignore")
            for i in range(0,len(text),self.chunk_chars):
                chunk=text[i:i+self.chunk_chars].strip()
                if chunk:
                    yield {
                        "source":str(p),
                        "chunk":i//self.chunk_chars,
                        "text":chunk
                    }

    def search(self,query):
        chunks=list(self._chunks())
        q=self._tokens(query.text)
        scored=[]

        for item in chunks:
            score=len(q & self._tokens(item["text"]))
            if score:
                x=dict(item)
                x["score"]=score
                x["retrieval_mode"]="lexical"
                scored.append(x)

        scored.sort(key=lambda x:x["score"],reverse=True)

        if scored:
            return KnowledgeResult(items=scored[:query.top_k])

        if self.fallback_on_empty and chunks:
            fallback=[]
            for item in chunks[:query.top_k]:
                x=dict(item)
                x["score"]=0
                x["retrieval_mode"]="fallback"
                fallback.append(x)
            return KnowledgeResult(items=fallback)

        return KnowledgeResult(items=[])
