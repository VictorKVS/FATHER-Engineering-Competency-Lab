import json
from pathlib import Path
from father.contracts.types import InputEvent

class ApiInputAdapter:
    def normalize(self,payload):
        return InputEvent(
            source="api",
            type=payload.get("type","message"),
            content=payload.get("content",""),
            metadata=payload.get("metadata",{})
        )

class FileInputAdapter:
    def normalize(self,path):
        p=Path(path)
        return InputEvent(
            source="file",
            type="message",
            content=p.read_text(encoding="utf-8"),
            metadata={"path":str(p)}
        )

class JsonOutputAdapter:
    def emit(self,result):
        return json.dumps({
            "ok":result.ok,
            "content":result.content,
            "metadata":result.metadata
        },ensure_ascii=False)

class FileOutputAdapter:
    def emit(self,result,path):
        p=Path(path)
        p.parent.mkdir(parents=True,exist_ok=True)
        payload={
            "ok":result.ok,
            "content":result.content,
            "metadata":result.metadata
        }
        p.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        return str(p)
