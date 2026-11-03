import json
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter, FileInputAdapter, JsonOutputAdapter, FileOutputAdapter
from father.core.knowledge import FolderKnowledge
from father.core.scoring import score_response

BASE=Path(__file__).resolve().parent
assembler=AgentAssembler(BASE)

evidence={
    "stage":"FATHER Chassis v1.6 / Stage 7",
    "goal":"prove the minimal end-to-end replaceable chassis without core rewrite",
    "checks":[],
    "runs":[]
}

def add_check(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return bool(passed)

def finish():
    ok=all(x["passed"] for x in evidence["checks"])
    evidence["result"]="PASS" if ok else "FAIL"
    out=BASE/"evidence/stage7_evidence.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\nRESULT:",evidence["result"])
    print("EVIDENCE:",out)
    raise SystemExit(0 if ok else 1)

print("=== BACKEND PREFLIGHT ===")
health=assembler.brain("qwen-analysis").health()
add_check("ollama_health",health.get("status")=="ok",health)
if health.get("status")!="ok":
    finish()

api=ApiInputAdapter()
file_in=FileInputAdapter()
json_out=JsonOutputAdapter()
file_out=FileOutputAdapter()

print("\n=== ASSEMBLE GENERIC AGENT ===")
agent,_=assembler.assemble(BASE/"config/agents/father_lab.json")
generic=assembler.competency("generic")
generic_prompt=agent.prompt_slot.system_prompt
add_check("agent_assembled",agent.agent_id=="father-lab-agent",{
    "agent_id":agent.agent_id,
    "brain_id":agent.brain.brain_id,
    "competency_id":agent.competency_id
})

print("\n=== API INPUT + GENERIC KNOWLEDGE ===")
generic_test=generic.tests[0]
api_event=api.normalize({"content":generic_test["prompt"],"metadata":{"stage":7}})
api_result=agent.run(api_event)
api_score=score_response(api_result.content,generic_test["rubric"])
evidence["runs"].append({
    "name":"api_generic",
    "brain_id":api_result.metadata.get("brain_id"),
    "knowledge_sources":api_result.metadata.get("knowledge_sources"),
    "quality":api_score,
    "response":api_result.content
})
add_check("api_input_adapter",api_event.source=="api" and api_event.content==generic_test["prompt"],{
    "source":api_event.source,
    "content":api_event.content
})
add_check("generic_knowledge_delivery",api_result.ok and (api_result.metadata.get("knowledge_hits") or 0)>0,{
    "hits":api_result.metadata.get("knowledge_hits"),
    "sources":api_result.metadata.get("knowledge_sources"),
    "modes":api_result.metadata.get("knowledge_modes")
})
add_check("generic_quality",api_score["passed"],api_score)

print("\n=== JSON OUTPUT ===")
json_payload=json_out.emit(api_result)
parsed=json.loads(json_payload)
add_check("json_output_adapter",parsed.get("ok") is True and bool(parsed.get("content")),{
    "bytes":len(json_payload.encode("utf-8"))
})

print("\n=== FILE INPUT + FILE OUTPUT ===")
input_path=BASE/"data/stage7_input.txt"
input_path.parent.mkdir(parents=True,exist_ok=True)
input_path.write_text(generic.tests[1]["prompt"],encoding="utf-8")
file_event=file_in.normalize(input_path)
file_result=agent.run(file_event)
file_score=score_response(file_result.content,generic.tests[1]["rubric"])
output_path=BASE/"evidence/stage7_file_output.json"
written=file_out.emit(file_result,output_path)
evidence["runs"].append({
    "name":"file_generic",
    "brain_id":file_result.metadata.get("brain_id"),
    "quality":file_score,
    "response":file_result.content
})
add_check("file_input_adapter",file_event.source=="file" and file_event.content==generic.tests[1]["prompt"],{
    "source":file_event.source,
    "path":file_event.metadata.get("path")
})
add_check("file_output_adapter",Path(written).exists() and Path(written).stat().st_size>0,{
    "path":written,
    "bytes":Path(written).stat().st_size
})
add_check("file_path_quality",file_score["passed"],file_score)

print("\n=== TOOL SLOT ===")
tool_result=agent.call_tool("calculator",{"a":7,"b":6,"op":"*"})
add_check("agent_to_tool",tool_result.ok and tool_result.result==42,{
    "tool":tool_result.name,
    "ok":tool_result.ok,
    "result":tool_result.result,
    "error":tool_result.error
})

print("\n=== COMPETENCY + PROMPT + KNOWLEDGE SWAP ===")
before_sources=api_result.metadata.get("knowledge_sources") or []
ib=assembler.competency("ib_demo")
swap=agent.apply_competency(ib,FolderKnowledge(ib.knowledge_dir,fallback_on_empty=True))
ib_prompt=agent.prompt_slot.system_prompt
ib_event=api.normalize({"content":ib.tests[0]["prompt"]})
ib_result=agent.run(ib_event)
ib_score=score_response(ib_result.content,ib.tests[0]["rubric"])
after_sources=ib_result.metadata.get("knowledge_sources") or []
evidence["runs"].append({
    "name":"ib_after_competency_swap",
    "brain_id":ib_result.metadata.get("brain_id"),
    "knowledge_sources":after_sources,
    "quality":ib_score,
    "response":ib_result.content
})
add_check("competency_swap",swap.get("old")!=swap.get("new") and agent.competency_id==ib.id,{
    "swap":swap,
    "current":agent.competency_id
})
add_check("prompt_swap",generic_prompt!=ib_prompt,{
    "generic_prompt":generic_prompt,
    "ib_prompt":ib_prompt
})
add_check("knowledge_swap",before_sources!=after_sources and any("ib_demo" in str(x) for x in after_sources),{
    "before":before_sources,
    "after":after_sources
})
add_check("ib_quality_after_swap",ib_result.ok and ib_score["passed"],ib_score)

print("\n=== BRAIN HOT SWAP ===")
brain_swap=agent.swap_brain(assembler.brain("llama-small"))
llama_result=agent.run(ib_event)
llama_score=score_response(llama_result.content,ib.tests[0]["rubric"])
evidence["runs"].append({
    "name":"ib_after_brain_swap",
    "brain_id":llama_result.metadata.get("brain_id"),
    "quality":llama_score,
    "response":llama_result.content
})
add_check("brain_hot_swap",brain_swap.get("old")=="qwen-analysis" and brain_swap.get("new")=="llama-small" and llama_result.metadata.get("brain_id")=="llama-small",{
    "swap":brain_swap,
    "result_brain":llama_result.metadata.get("brain_id")
})
add_check("brain_swap_preserves_competency",llama_result.ok and llama_score["passed"] and llama_result.metadata.get("competency_id")==ib.id,{
    "competency_id":llama_result.metadata.get("competency_id"),
    "knowledge_hits":llama_result.metadata.get("knowledge_hits"),
    "quality":llama_score
})

print("\n=== MINIMAL CHASSIS RELEASE GATE ===")
required=[
    "ollama_health","agent_assembled","api_input_adapter","generic_knowledge_delivery",
    "generic_quality","json_output_adapter","file_input_adapter","file_output_adapter",
    "file_path_quality","agent_to_tool","competency_swap","prompt_swap","knowledge_swap",
    "ib_quality_after_swap","brain_hot_swap","brain_swap_preserves_competency"
]
present={x["name"]:x["passed"] for x in evidence["checks"]}
release=all(present.get(x) is True for x in required)
add_check("minimal_chassis_v1_release_gate",release,{
    "required":required,
    "passed":[x for x in required if present.get(x) is True],
    "failed":[x for x in required if present.get(x) is not True]
})

finish()
