import hashlib,json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOTS=[BASE/"father",BASE/"config"]
rows=[]
for root in ROOTS:
    for p in root.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix.lower() in {".py",".json",".md",".txt"}:
            rows.append({"path":p.relative_to(BASE).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
rows=sorted(rows,key=lambda x:x["path"])

release_path=BASE/"evidence/stage19_release_manifest.json"
release=json.loads(release_path.read_text(encoding="utf-8"))
bom={"release_version":release["release_version"],"release_manifest_digest":release["manifest_digest"],"external_anchor_commit":release["external_anchor"]["commit"],"files":rows}
bom["bom_digest"]=hashlib.sha256(json.dumps(bom,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

checks=[]
def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}; checks.append(item); print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))

add("release_manifest_loaded",bool(release.get("manifest_digest")),{"release_version":release.get("release_version"),"manifest_digest":release.get("manifest_digest")})
add("bom_has_files",len(rows)>10,{"files":len(rows)})
add("bom_bound_to_release",bom["release_manifest_digest"]==release["manifest_digest"],{"release_manifest_digest":bom["release_manifest_digest"]})
add("bom_bound_to_external_anchor",bool(bom["external_anchor_commit"]),{"external_anchor_commit":bom["external_anchor_commit"]})

bad=json.loads(json.dumps(bom))
bad["files"][0]["sha256"]="0"*64
bad_digest=hashlib.sha256(json.dumps({k:v for k,v in bad.items() if k!="bom_digest"},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
add("bom_detects_record_change",bad_digest!=bad["bom_digest"],{"expected":bad_digest,"actual":bad["bom_digest"]})

first=BASE/bom["files"][0]["path"]
actual=hashlib.sha256(first.read_bytes()).hexdigest()
add("bom_file_hash_matches",actual==bom["files"][0]["sha256"],{"path":bom["files"][0]["path"],"sha256":actual})

result="PASS" if all(x["passed"] for x in checks) else "FAIL"
evidence={"stage":"FATHER Chassis v2.9 / Stage 20","goal":"release seal and bill of materials","checks":checks,"result":result,"bom_digest":bom["bom_digest"]}
(BASE/"evidence/stage20_bom.json").write_text(json.dumps(bom,ensure_ascii=False,indent=2),encoding="utf-8")
(BASE/"evidence/stage20_evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESULT:",result)
print("BOM:",BASE/"evidence/stage20_bom.json")
raise SystemExit(0 if result=="PASS" else 1)
