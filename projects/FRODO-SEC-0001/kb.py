#!/usr/bin/env python3
"""FRODO knowledge pack: offline read-only search and consistency checks.

No network calls, model inference, vulnerability scanning, or tool execution.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "knowledge"

def read(name):
    return json.loads((DB / name).read_text(encoding="utf-8"))

def validate():
    nodes = read("llm_concepts.json")
    edges = read("llm_edges.json")
    sources = read("source_manifest.json")
    threats = read("threat_catalog.json")
    ids = [n["id"] for n in nodes]
    assert len(ids) == len(set(ids)), "duplicate node IDs"
    index = set(ids)
    for n in nodes:
        assert n["source_id"] == sources["id"]
        assert n["chapter"] in sources["reviewed_chapters"], n["id"]
        assert n["pages"][0] >= sources["reviewed_pdf_ranges"][n["chapter"]][0]
        assert n["pages"][1] <= sources["reviewed_pdf_ranges"][n["chapter"]][1]
    for e in edges:
        assert e["from"] in index and e["to"] in index, e
    for t in threats:
        assert t["topic_node"] in index, t["id"]
        assert t["control_node"] in index, t["id"]
        assert t["mode"] == "SANDBOX_SYNTHETIC_ONLY"
    return {"nodes": len(nodes), "edges": len(edges), "threats": len(threats),
            "chapters": len(sources["reviewed_chapters"]), "valid": True}

def search(text, limit=12):
    needle = text.casefold().strip()
    if not needle:
        return []
    nodes = read("llm_concepts.json")
    matches = [((4 if needle in n["title"].casefold() else 0) +
                (1 if needle in n["definition_ru"].casefold() else 0), n)
               for n in nodes]
    ranked = [(score, n) for score, n in matches if score > 0]
    ranked.sort(key=lambda x: (-x[0], -x[1]["weight"], x[1]["id"]))
    return [n for _, n in ranked[:limit]]

def main(args):
    cmd = args[0] if args else "stats"
    if cmd in {"check", "stats"}:
        print(json.dumps(validate(), ensure_ascii=False, indent=2))
    elif cmd == "search":
        if len(args) < 2:
            raise ValueError("Usage: python kb.py search <query>")
        for n in search(" ".join(args[1:])):
            print(f'{n["id"]} [{n["chapter"]}, PDF {n["pages"]}] {n["title"]}: {n["definition_ru"]}')
    elif cmd == "chapter":
        if len(args) != 2:
            raise ValueError("Usage: python kb.py chapter CH01")
        nodes = [n for n in read("llm_concepts.json") if n["chapter"] == args[1]]
        print(json.dumps(nodes, ensure_ascii=False, indent=2))
    elif cmd == "threats":
        for t in read("threat_catalog.json"):
            print(f'{t["id"]} {t["name"]}: {t["expected"]}')
    else:
        raise ValueError("commands: stats | check | search <text> | chapter <CHxx> | threats")

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (AssertionError, ValueError, OSError) as exc:
        print("FRODO KB ERROR:", exc, file=sys.stderr)
        sys.exit(1)
