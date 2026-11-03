import json
import time
from pathlib import Path

class WorkflowOrchestrator:
    def __init__(self, router, assembler, audit_path):
        self.router=router
        self.assembler=assembler
        self.audit_path=Path(audit_path)
        self.audit_path.parent.mkdir(parents=True,exist_ok=True)

    def _audit(self, run_id, stage, status, details):
        row={
            "run_id":run_id,
            "ts_ms":int(time.time()*1000),
            "stage":stage,
            "status":status,
            "details":details
        }
        with self.audit_path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return row

    def run(self, event, task_type, tool_call=None):
        run_id=f"wf-{int(time.time()*1000)}"
        state={
            "run_id":run_id,
            "status":"started",
            "task_type":task_type,
            "event_source":event.source,
            "route":None,
            "agent_id":None,
            "brain_id":None,
            "competency_id":None,
            "knowledge_hits":0,
            "tool":None,
            "result":None,
            "transitions":[]
        }

        def step(name,status,details):
            state["transitions"].append({
                "stage":name,
                "status":status,
                "details":details
            })
            self._audit(run_id,name,status,details)

        step("event","ok",{
            "source":event.source,
            "type":event.type,
            "metadata":event.metadata
        })

        route=self.router.route(task_type)
        state["route"]=route
        state["agent_id"]=route["agent_id"]
        step("route","ok",route)

        agent,_=self.assembler.assemble(route["manifest_path"])
        state["brain_id"]=agent.brain.brain_id
        state["competency_id"]=agent.competency_id
        step("assemble","ok",{
            "agent_id":agent.agent_id,
            "brain_id":agent.brain.brain_id,
            "competency_id":agent.competency_id
        })

        if tool_call:
            tool_result=agent.call_tool(tool_call["name"],tool_call.get("arguments",{}))
            state["tool"]={
                "name":tool_result.name,
                "ok":tool_result.ok,
                "result":tool_result.result,
                "error":tool_result.error
            }
            step("tool","ok" if tool_result.ok else "error",state["tool"])
            if not tool_result.ok:
                state["status"]="failed"
                return state

        result=agent.run(event)
        state["result"]={
            "ok":result.ok,
            "content":result.content,
            "metadata":result.metadata
        }
        state["knowledge_hits"]=result.metadata.get("knowledge_hits",0)
        step("agent","ok" if result.ok else "error",{
            "agent_id":agent.agent_id,
            "brain_id":result.metadata.get("brain_id"),
            "competency_id":result.metadata.get("competency_id"),
            "knowledge_hits":result.metadata.get("knowledge_hits"),
            "error":result.metadata.get("error")
        })

        state["status"]="completed" if result.ok else "failed"
        step("complete",state["status"],{
            "agent_id":state["agent_id"],
            "brain_id":state["brain_id"],
            "tool_used":bool(tool_call)
        })
        return state
