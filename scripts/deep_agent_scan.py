from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
import argparse
import hashlib
import json
import os
import string

TEXT_EXTS={".md",".yaml",".yml",".json",".toml",".py",".txt"}
SKIP_DIRS={
    "node_modules",".git",".svn",".hg","__pycache__",".venv","venv","env",".cache",
    ".pytest_cache",".mypy_cache",".ruff_cache","dist","build","site-packages",
    "$recycle.bin","system volume information","windows","program files","program files (x86)","programdata"
}
STRONG_MARKERS=("agent_id","role:","capabilities:","prompt","rag_manifest","knowledge_base","tools:","permissions:","evals:")
WEAK_MARKERS=("agent","assistant","workflow","planner","executor","autopilot","copilot")
PROJECT_MARKERS=("README.md","pyproject.toml","requirements.txt","package.json","agent.yaml","agent.yml","AGENTS.md")


@dataclass(frozen=True)
class Candidate:
    id:str
    root:str
    score:int
    confidence:str
    evidence:tuple[str,...]


def cid(path:str)->str:
    return "DEEP-"+hashlib.sha256(path.encode("utf-8")).hexdigest()[:12].upper()


def roots_all():
    out=[]
    for letter in string.ascii_uppercase:
        p=f"{letter}:\\"
        if os.path.exists(p):
            out.append(p)
    return out


def scan_project_dir(path:Path)->Candidate|None:
    evidence=[]
    score=0
    names={p.name for p in path.iterdir() if p.is_file()}
    for m in PROJECT_MARKERS:
        if m in names:
            evidence.append("project:"+m)
            score+=2

    inspected=0
    for p in path.iterdir():
        if inspected>=30: break
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS: continue
        inspected+=1
        try:
            txt=p.read_text(encoding="utf-8",errors="ignore")[:50000].lower()
        except OSError:
            continue
        local=[]
        for marker in STRONG_MARKERS:
            if marker.lower() in txt:
                local.append(marker)
                score+=3
        for marker in WEAK_MARKERS:
            if marker.lower() in txt:
                local.append(marker)
                score+=1
        if local:
            evidence.append(f"{p.name}:"+",".join(sorted(set(local))))

    if score<7:
        return None
    confidence="CANONICAL" if score>=24 else "HIGH" if score>=15 else "MEDIUM"
    return Candidate(cid(str(path)),str(path),score,confidence,tuple(evidence[:30]))


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
            current_path=Path(current)
            # Only inspect plausible project directories.
            names=set(files)
            plausible=bool(names.intersection(PROJECT_MARKERS)) or any("agent" in x.lower() for x in names)
            if not plausible:
                continue
            key=str(current_path).lower()
            if key in seen: continue
            seen.add(key)
            try:
                cand=scan_project_dir(current_path)
            except OSError:
                errors+=1
                continue
            if cand:
                candidates.append(cand)
        stats.append({"root":str(root),"directories_seen":dirs_seen,"errors":errors})

    candidates.sort(key=lambda x:(-x.score,x.root.lower()))
    return {
        "schema":"FATHER_DEEP_AGENT_SCAN_V1",
        "mode":"READ_ONLY",
        "count":len(candidates),
        "candidates":[asdict(x) for x in candidates],
        "sources":stats,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("roots",nargs="*",help="Roots to scan; default = all Windows drives")
    ap.add_argument("--out",default="deep-agent-scan.json")
    args=ap.parse_args()
    roots=args.roots or roots_all()
    result=deep_scan(roots)
    out=Path(args.out)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({
        "schema":result["schema"],
        "roots":roots,
        "count":result["count"],
        "output":str(out.resolve()),
        "top":[{"root":x["root"],"score":x["score"],"confidence":x["confidence"]} for x in result["candidates"][:20]]
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
