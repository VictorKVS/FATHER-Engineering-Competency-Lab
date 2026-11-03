import json
from pathlib import Path

class RuntimeJsonOutputAdapter:
    def emit(self,payload):
        return json.dumps(payload,ensure_ascii=False)

class RuntimeFileOutputAdapter:
    def emit(self,payload,path):
        p=Path(path)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        return str(p)
