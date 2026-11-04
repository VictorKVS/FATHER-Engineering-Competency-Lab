import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
manifest=json.loads((BASE/"config/agents/father_story.json").read_text(encoding="utf-8"))
zoo=json.loads((BASE/"config/agent_zoo.json").read_text(encoding="utf-8"))
server=(BASE/"story_studio_server.py").read_text(encoding="utf-8")
html=(BASE/"story_studio_web/index.html").read_text(encoding="utf-8")
js=(BASE/"story_studio_web/app.js").read_text(encoding="utf-8")

checks=[]
def check(name,ok,details):
    checks.append({"name":name,"passed":bool(ok),"details":details})
    print(("PASS" if ok else "FAIL"),name,json.dumps(details,ensure_ascii=False))

check("single_llm_fixed",
      manifest.get("single_llm") is True
      and manifest.get("runtime_model")=="qwen2.5:7b"
      and manifest.get("brain_id")=="qwen-analysis"
      and 'MODEL="qwen2.5:7b"' in server,
      manifest)

entry=zoo["agents"].get("father-story-agent",{})
check("agent_zoo_registered",
      entry.get("supported_brains")==["qwen-analysis"]
      and entry.get("role")=="creative-writer",
      entry)

modes={"CONTINUE","REWRITE","SIMILAR","EDIT"}
check("story_modes_present",
      all(x in html and x in server for x in modes),
      {"modes":sorted(modes)})

check("text_upload_and_clarification_present",
      'type="file"' in html
      and 'id="instruction"' in html
      and "history" in js,
      {"file_upload":True,"clarification":True,"session_history":True})

ok=all(x["passed"] for x in checks)
evidence={"milestone":"FATHER STORY AGENT MVP-01","result":"PASS" if ok else "FAIL","checks":checks}
out=BASE/"evidence/story_agent_mvp01.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if ok else 1)
