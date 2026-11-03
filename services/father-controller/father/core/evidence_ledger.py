import json
from pathlib import Path
from father.core.provenance import digest

class EvidenceLedger:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def rows(self):
        if not self.path.exists():
            return []
        out=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def append(self,bundle):
        rows=self.rows()
        seq=len(rows)+1
        prev_hash=rows[-1]["entry_hash"] if rows else "GENESIS"
        payload={
            "seq":seq,
            "run_id":bundle.get("run_id"),
            "bundle_digest":bundle.get("bundle_digest"),
            "prev_hash":prev_hash
        }
        entry_hash=digest(payload)
        row={**payload,"entry_hash":entry_hash}
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return row

    def verify(self):
        rows=self.rows()
        issues=[]
        expected_prev="GENESIS"

        for index,row in enumerate(rows,1):
            if row.get("seq")!=index:
                issues.append({"seq":index,"kind":"sequence","actual":row.get("seq")})

            if row.get("prev_hash")!=expected_prev:
                issues.append({
                    "seq":index,
                    "kind":"previous_hash",
                    "expected":expected_prev,
                    "actual":row.get("prev_hash")
                })

            payload={
                "seq":row.get("seq"),
                "run_id":row.get("run_id"),
                "bundle_digest":row.get("bundle_digest"),
                "prev_hash":row.get("prev_hash")
            }
            calculated=digest(payload)
            if row.get("entry_hash")!=calculated:
                issues.append({
                    "seq":index,
                    "kind":"entry_hash",
                    "expected":calculated,
                    "actual":row.get("entry_hash")
                })

            expected_prev=row.get("entry_hash")

        return {
            "ok":len(rows)>0 and not issues,
            "entries":len(rows),
            "head_hash":rows[-1]["entry_hash"] if rows else None,
            "issues":issues
        }
