from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
import argparse
import hashlib
import json
import os
import string

TEXT_EXTS={".md",".yaml",".yml",".json",".toml",".py",".txt",".ps1",".js",".ts"}
SKIP_DIRS={
    "node_modules",".git",".svn",".hg","__pycache__",".venv","venv","env",".cache",
    ".pytest_cache",".mypy_cache",".ruff_cache","dist","build","site-packages",
    "$recycle.bin","system volume information","windows","program files","program files (x86)","programdata"
}
DOC_DIR_NAMES={"docs","documentation","reference","references","tutorial","tutorials","examples","example","knowledge_base","knowledge","tests","test"}
MANIFEST_FILES={"agent.yaml","agent.yml","agent.json","AGENTS.md","agent.toml"}
PROJECT_FILES={"pyproject.toml","requirements.txt","package.json","setup.py","setup.cfg","Pipfile","poetry.lock"}
EXECUTABLE_NAMES={"main.py","app.py","run.py","runner.py","executor.py","agent.py","server.py","cli.py"}
STRONG_MARKERS=("agent_id","role:","capabilities:","prompt","rag_manifest","knowledge_base","tools:","permissions:","evals:")
RUNTIME_MARKERS=("executor","runner","workflow","planner","invoke","generate","chat","tool_call","model_adapter","runtime")
WEAK_MARKERS=("agent","assistant","autopilot","copilot")


@dataclass(frozen=True)
class Candidate:
    id:str
    root:str
    score:int
    confidence:str
    kind:str
    evidence:tuple[str,...]


def cid(path:str)->str:
    return "DEEP-"+hashlib.sha256(path.encode("utf-8")).hexdigest()[:12].upper()


def roots_all():
    return [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]


def classify_dir(path:Path, files:list[str])->Candidate|None:
    lower_parts={p.lower() for p in path.parts}
    docish=bool(lower_parts.intersection(DOC_DIR_NAMES))
    names=set(files)
    score=0
    evidence=[]
    strong_count=0
    runtime_count=0
    has_manifest=bool(names.intersection(MANIFEST_FILES))
    has_project=bool(names.intersection(PROJECT_FILES))
    has_exec=bool(names.intersection(EXECUTABLE_NAMES))

    if has_manifest:
        score+=18
        evidence.append("manifest:"+",".join(sorted(names.intersection(MANIFEST_FILES))))
    if has_project:
        score+=5
        evidence.append("project:"+",".join(sorted(names.intersection(PROJECT_FILES))))
    if has_exec:
        score+=8
        evidence.append("runtime_file:"+",".join(sorted(names.intersection(EXECUTABLE_NAMES))))

    inspected=0
    for p in path.iterdir():
        if inspected>=40:
            break
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        inspected+=1
        try:
            txt=p.read_text(encoding="utf-8",errors="ignore")[:60000].lower()
        except OSError:
            continue
        local=[]
        for marker in STRONG_MARKERS:
            if marker.lower() in txt:
                local.append(marker)
                strong_count+=1
                score+=3
        for marker in RUNTIME_MARKERS:
            if marker.lower() in txt:
                local.append(marker)
                runtime_count+=1
                score+=2
        for marker in WEAK_MARKERS:
            if marker.lower() in txt:
                local.append(marker)
                score+=1
        if local:
            evidence.append(f"{p.name}:"+",".join(sorted(set(local))))

    # Penalize directories that are overwhelmingly documentation/reference/tests.
    if docish and not has_manifest and not has_exec:
        score-=18
        evidence.append("penalty:documentation_or_test_area")

    # Require structural evidence, not just vocabulary.
    if not (has_manifest or has_exec or (has_project and strong_count>=3 and runtime_count>=2)):
        return None
    if score<12:
        return None

    if has_manifest and (has_exec or runtime_count>=2):
        kind="AGENT"
    elif has_manifest or (has_project and has_exec):
        kind="AGENT_ASSET"
    elif docish:
        kind="DOCUMENTATION"
    else:
        kind="AGENT_CANDIDATE"

    confidence="CANONICAL" if score>=32 and kind=="AGENT" else "HIGH" if score>=22 else "MEDIUM"
    return Candidate(cid(str(path)),str(path),score,confidence,kind,tuple(evidence[:40]))


def deep_scan(roots):
    candidates=[]
    seen=set()
    stats=[]
    for root_value in roots:
        root=Path(root_value)
        dirs_seen=0
        errors=0
        for current, dirs, files in os.walk(root,topdown=True,onerror=lambda _e: None):
            dirs[:]=[d for d in dirs if d.lower() not in SKIP_DIRS]
            dirs_seen+=1
            names=set(files)
            plausible=bool(names.intersection(MANIFEST_FILES|PROJECT_FILES|EXECUTABLE_NAMES)) or any("agent" in x.lower() for x in files)
            if not plausible:
                continue
            current_path=Path(current)
            key=str(current_path).lower()
            if key in seen:
                continue
            seen.add(key)
            try:
                cand=classify_dir(current_path,files)
            except OSError:
                errors+=1
                continue
            if cand:
                candidates.append(cand)
        stats.append({"root":str(root),"directories_seen":dirs_seen,"errors":errors})

    candidates.sort(key=lambda x:(0 if x.kind=="AGENT" else 1 if x.kind=="AGENT_ASSET" else 2,-x.score,x.root.lower()))
    counts={}
    for x in candidates:
        counts[x.kind]=counts.get(x.kind,0)+1
    return {
        "schema":"FATHER_DEEP_AGENT_SCAN_V2",
        "mode":"READ_ONLY",
        "count":len(candidates),
        "kind_counts":counts,
        "candidates":[asdict(x) for x in candidates],
        "sources":stats,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("roots",nargs="*",help="Roots to scan; default = all Windows drives")
    ap.add_argument("--out",default="deep-agent-scan-v2.json")
    args=ap.parse_args()
    roots=args.roots or roots_all()
    result=deep_scan(roots)
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({
        "schema":result["schema"],
        "roots":roots,
        "count":result["count"],
        "kind_counts":result["kind_counts"],
        "output":str(out.resolve()),
        "top":[
            {"root":x["root"],"score":x["score"],"confidence":x["confidence"],"kind":x["kind"]}
            for x in result["candidates"][:30]
        ]
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
