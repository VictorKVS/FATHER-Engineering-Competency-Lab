from pathlib import Path
import re
from father.contracts.types import KnowledgeResult

class NullKnowledge:
    def health(self): return {"status":"ok","adapter":"null","documents":0}
    def search(self,query): return KnowledgeResult(items=[])

class FolderKnowledge:
    def __init__(self,folder,chunk_chars=1800):
        self.folder=Path(folder); self.chunk_chars=chunk_chars
    def health(self):
        fs=list(self.folder.glob("**/*.md"))+list(self.folder.glob("**/*.txt"))
        return {"status":"ok" if self.folder.exists() else "error","adapter":"folder","documents":len(fs)}
    @staticmethod
    def _tokens(text):
        return set(re.findall(r"[A-Za-zА-Яа-яЁё0-9_-]{3,}",text.lower()))
    def _chunks(self):
        for p in list(self.folder.glob("**/*.md"))+list(self.folder.glob("**/*.txt")):
            text=p.read_text(encoding="utf-8",errors="ignore")
            for i in range(0,len(text),self.chunk_chars):
                chunk=text[i:i+self.chunk_chars].strip()
                if chunk: yield {"source":str(p),"chunk":i//self.chunk_chars,"text":chunk}
    def search(self,query):
        q=self._tokens(query.text); scored=[]
        for item in self._chunks():
            score=len(q & self._tokens(item["text"]))
            if score:
                x=dict(item); x["score"]=score; scored.append(x)
        scored.sort(key=lambda x:x["score"],reverse=True)
        return KnowledgeResult(items=scored[:query.top_k])
