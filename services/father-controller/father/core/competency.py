import json
from pathlib import Path
class CompetencyPack:
    def __init__(self,pack_dir):
        self.pack_dir=Path(pack_dir)
        self.manifest=json.loads((self.pack_dir/"manifest.json").read_text(encoding="utf-8"))
    @property
    def id(self): return self.manifest["id"]
    @property
    def version(self): return self.manifest.get("version","0")
    @property
    def system_prompt(self): return self.manifest.get("system_prompt","")
    @property
    def knowledge_dir(self): return str(self.pack_dir/self.manifest.get("knowledge_dir","knowledge"))
    @property
    def tests(self): return self.manifest.get("tests",[])
