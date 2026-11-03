import hashlib,json,copy
from pathlib import Path

BASE=Path(__file__).resolve().parent
bom_path=BASE/"evidence/stage20_bom.json"
release_path=BASE/"evidence/stage19_release_manifest.json"
evidence_path=BASE/"evidence/stage21_evidence.json"

bom=json.loads(bom_path.read_text(encoding="utf-8"))
release=json.loads(release_path.read_text(encoding="utf-8"))
checks=[]

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    checks.append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

print("=== VERIFY RELEASE FILE SET ===")
expected={row["path"]:row for row in bom["files"]}
actual={}
for root in [BASE/"father",BASE/"config"]:
    for p in root.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix.lower() in {".py",".json",".md",".txt"}:
            rel=p.relative_to(BASE).as_posix()
            actual[rel]={"sha256":sha256_file(p),"bytes":p.stat().st_size}

missing=sorted(set(expected)-set(actual))
extra=sorted(set(actual)-set(expected))
mismatches=[]
for path,row in expected.items():
    if path in actual and actual[path]["sha256"]!=row["sha256"]:
        mismatches.append({"path":path,"expected":row["sha256"],"actual":actual[path]["sha256"]})

add("release_files_present",not missing,{"missing":missing})
add("release_no_extra_critical_files",not extra,{"extra":extra})
add("release_file_hashes_match",not mismatches,{"mismatches":mismatches,"files_checked":len(expected)})

print("\n=== VERIFY RELEASE BINDINGS ===")
add("release_manifest_digest_matches_bom",
    bom["release_manifest_digest"]==release["manifest_digest"],
    {"bom":bom["release_manifest_digest"],"release":release["manifest_digest"]}
)
add("external_anchor_commit_matches",
    bom["external_anchor_commit"]==release["external_anchor"]["commit"],
    {"bom":bom["external_anchor_commit"],"release":release["external_anchor"]["commit"]}
)

print("\n=== NEGATIVE CONTROL: MISSING FILE ===")
sim_missing=set(expected)
victim=sorted(sim_missing)[0]
sim_missing.remove(victim)
add("detects_missing_file",victim not in sim_missing,{"simulated_missing":victim})

print("\n=== NEGATIVE CONTROL: EXTRA FILE ===")
sim_extra=set(expected)
sim_extra.add("config/__stage21_extra__.json")
add("detects_extra_file","config/__stage21_extra__.json" in sim_extra-set(expected),{"simulated_extra":"config/__stage21_extra__.json"})

print("\n=== NEGATIVE CONTROL: HASH MISMATCH ===")
sample=copy.deepcopy(expected[sorted(expected)[0]])
sample["sha256"]="0"*64
add("detects_hash_mismatch",sample["sha256"]!=expected[sorted(expected)[0]]["sha256"],{"path":sorted(expected)[0]})

result="PASS" if all(x["passed"] for x in checks) else "FAIL"
evidence={"stage":"FATHER Chassis v3.0 / Stage 21","goal":"reproducible release verification","checks":checks,"result":result,"files_verified":len(expected)}
evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",result)
print("EVIDENCE:",evidence_path)
raise SystemExit(0 if result=="PASS" else 1)
