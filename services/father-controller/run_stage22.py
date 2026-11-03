import json
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter, FileInputAdapter
from father.core.runtime_io import RuntimeJsonOutputAdapter, RuntimeFileOutputAdapter
from father.core.unified_runtime import UnifiedAgentRuntime

BASE=Path(__file__).resolve().parent
PROFILE=json.loads((BASE/"config/runtime_profiles/single_llm.json").read_text(encoding="utf-8"))
assembler=AgentAssembler(BASE)
manifest=BASE/PROFILE["agent_manifest"]
agent,_=assembler.assemble(manifest)
runtime=UnifiedAgentRuntime(agent,top_k=PROFILE["retrieval"]["top_k"])

api=ApiInputAdapter()
file_in=FileInputAdapter()
json_out=RuntimeJsonOutputAdapter()
file_out=RuntimeFileOutputAdapter()

evidence={
    "stage":"FATHER Chassis v3.1 / Stage 22",
    "goal":"prove one complete configurable agent runtime with one LLM",
    "profile":PROFILE,
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== PROFILE / SLOTS ===")
add("profile_loaded",PROFILE["profile_id"]=="father-single-llm-v1",PROFILE)
add("single_brain_bound",agent.brain.brain_id==PROFILE["brain_id"],{
    "brain_id":agent.brain.brain_id,
    "competency_id":agent.competency_id
})
add("brain_slot_swappable",callable(getattr(agent,"swap_brain",None)),{
    "method":"swap_brain"
})
add("prompt_slot_loaded",bool(agent.prompt_slot.system_prompt),{
    "prompt":agent.prompt_slot.system_prompt
})
add("knowledge_slot_loaded",agent.knowledge.health()["status"]=="ok",agent.knowledge.health())

print("\n=== API INPUT -> RAG/KNOWLEDGE -> LLM -> JSON OUTPUT ===")
event=api.normalize({
    "type":"architecture",
    "content":"Что такое Brain Slot в FATHER?",
    "metadata":{"stage":22}
})
result=runtime.run(event,"architecture")
rendered=json_out.emit(result)
add("api_pipeline_completed",result["ok"] and result["input_source"]=="api",{
    "ok":result["ok"],
    "brain_id":result["brain_id"],
    "knowledge_hits":result["knowledge_hits"]
})
add("knowledge_injected",result["knowledge_hits"]>0 and bool(result["knowledge_sources"]),{
    "hits":result["knowledge_hits"],
    "sources":result["knowledge_sources"],
    "modes":result["knowledge_modes"]
})
add("json_output_emitted",rendered.startswith("{") and '"content"' in rendered,{
    "chars":len(rendered)
})
add("context_envelope_created",
    result["envelope"]["task_id"]==result["task_id"]
    and result["envelope"]["producer"]==result["brain_id"]
    and bool(result["envelope"]["history"]),
    {
        "task_id":result["task_id"],
        "producer":result["envelope"]["producer"],
        "history_items":len(result["envelope"]["history"])
    }
)

print("\n=== TOOL SLOT -> CONTEXT -> LLM ===")
tool_event=api.normalize({
    "type":"architecture",
    "content":"Используй результат инструмента и скажи чему равно 6 умножить на 7.",
    "metadata":{"stage":22}
})
tool_result=runtime.run(
    tool_event,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":6,"b":7,"op":"*"}}
)
add("tool_slot_integrated",
    tool_result["tool"] is not None
    and tool_result["tool"]["ok"]
    and tool_result["tool"]["result"]==42,
    tool_result["tool"]
)
add("tool_result_passed_via_context",
    tool_result["envelope"]["artifacts"].get("tool_result",{}).get("result")==42,
    tool_result["envelope"]["artifacts"].get("tool_result")
)

print("\n=== FILE INPUT -> SAME AGENT -> FILE OUTPUT ===")
in_path=BASE/"evidence/stage22_input.txt"
out_path=BASE/"evidence/stage22_output.json"
in_path.parent.mkdir(parents=True,exist_ok=True)
in_path.write_text("Что такое Knowledge Slot в FATHER?",encoding="utf-8")
file_event=file_in.normalize(in_path)
file_result=runtime.run(file_event,"architecture")
written=file_out.emit(file_result,out_path)
add("file_input_supported",file_result["ok"] and file_result["input_source"]=="file",{
    "source":file_result["input_source"],
    "input_path":str(in_path)
})
add("file_output_supported",Path(written).exists() and Path(written).stat().st_size>0,{
    "output_path":written,
    "bytes":Path(written).stat().st_size
})

print("\n=== RAG MATURITY LABEL ===")
add("retrieval_mode_declared",
    PROFILE["retrieval"]["mode"]=="lexical-bootstrap"
    and PROFILE["retrieval"]["semantic_vector_ready"] is False,
    PROFILE["retrieval"]
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["runtime_result"]={
    "api_task_id":result["task_id"],
    "file_task_id":file_result["task_id"],
    "brain_id":result["brain_id"],
    "competency_id":result["competency_id"]
}

out=BASE/"evidence/stage22_evidence.json"
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("OUTPUT:",out_path)
raise SystemExit(0 if release else 1)
