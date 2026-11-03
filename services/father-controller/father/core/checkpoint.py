import hashlib
import hmac
import json
from pathlib import Path
from father.core.provenance import digest

class LedgerCheckpoint:
    def __init__(self,path,key):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.key=key.encode("utf-8") if isinstance(key,str) else bytes(key)

    def _mac(self,payload):
        data=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
        return hmac.new(self.key,data,hashlib.sha256).hexdigest()

    def create(self,ledger_status):
        payload={
            "entries":ledger_status.get("entries"),
            "head_hash":ledger_status.get("head_hash"),
            "ledger_ok":ledger_status.get("ok")
        }
        checkpoint={
            "payload":payload,
            "payload_digest":digest(payload),
            "hmac_sha256":self._mac(payload)
        }
        self.path.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding="utf-8")
        return checkpoint

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def verify(self,ledger_status,checkpoint=None):
        cp=checkpoint or self.load()
        payload=cp.get("payload",{})
        expected_mac=self._mac(payload)
        mac_ok=hmac.compare_digest(str(cp.get("hmac_sha256","")),expected_mac)
        digest_ok=cp.get("payload_digest")==digest(payload)
        ledger_match=(
            payload.get("entries")==ledger_status.get("entries")
            and payload.get("head_hash")==ledger_status.get("head_hash")
            and ledger_status.get("ok") is True
        )
        return {
            "ok":bool(mac_ok and digest_ok and ledger_match),
            "mac_ok":mac_ok,
            "digest_ok":digest_ok,
            "ledger_match":ledger_match,
            "checkpoint_entries":payload.get("entries"),
            "checkpoint_head":payload.get("head_hash"),
            "ledger_entries":ledger_status.get("entries"),
            "ledger_head":ledger_status.get("head_hash")
        }
