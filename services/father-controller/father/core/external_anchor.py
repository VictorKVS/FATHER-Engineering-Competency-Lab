import hashlib
import json
from pathlib import Path

class ExternalAnchor:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    @staticmethod
    def file_sha256(path):
        p=Path(path)
        h=hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                h.update(chunk)
        return h.hexdigest()

    def create(self,ledger_status,checkpoint_path):
        payload={
            "ledger_entries":ledger_status.get("entries"),
            "ledger_head_hash":ledger_status.get("head_hash"),
            "checkpoint_sha256":self.file_sha256(checkpoint_path)
        }
        self.path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        return payload

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def verify(self,ledger_status,checkpoint_path):
        anchor=self.load()
        expected={
            "ledger_entries":ledger_status.get("entries"),
            "ledger_head_hash":ledger_status.get("head_hash"),
            "checkpoint_sha256":self.file_sha256(checkpoint_path)
        }
        return {
            "ok":anchor==expected,
            "anchor":anchor,
            "expected":expected
        }
