import time
from father.contracts.types import BrainRequest, KnowledgeQuery
from father.core.context_bus import ContextEnvelope

class UnifiedAgentRuntime:
    def __init__(self, agent, top_k=5):
        self.agent=agent
        self.top_k=top_k

    def _retrieve(self, text):
        return self.agent.knowledge.search(
            KnowledgeQuery(text=str(text), top_k=self.top_k)
        ).items

    def _messages(self, envelope):
        messages=[]
        if self.agent.prompt_slot.system_prompt:
            messages.append({
                "role":"system",
                "content":self.agent.prompt_slot.system_prompt
            })

        if envelope.knowledge:
            kb_text="\n\n".join(
                f'[SOURCE: {x.get("source","?")} | MODE: {x.get("retrieval_mode","unknown")} | SCORE: {x.get("score",0)}]\n{x.get("text","")}'
                for x in envelope.knowledge
            )
            messages.append({
                "role":"system",
                "content":"Контекст RAG/Knowledge для текущей задачи. "
                          "Опирайся на источники, не выдумывай отсутствующие факты.\n\n"+kb_text
            })

        for item in envelope.history:
            if item.get("role") in ("user","assistant","system"):
                messages.append({
                    "role":item["role"],
                    "content":str(item.get("content",""))
                })

        messages.append({"role":"user","content":envelope.input_text})
        return messages

    def run(self, event, task_type="message", tool_call=None):
        task_id=f"agent-{int(time.time()*1000)}"
        envelope=ContextEnvelope(
            task_id=task_id,
            task_type=task_type,
            input_text=str(event.content),
            metadata={
                "input_source":event.source,
                "input_type":event.type,
                "input_metadata":event.metadata
            }
        )

        knowledge=self._retrieve(envelope.input_text)
        envelope.add_knowledge(knowledge)

        tool_result=None
        if tool_call:
            tool_result=self.agent.call_tool(
                tool_call["name"],
                tool_call.get("arguments",{})
            )
            envelope.artifacts["tool_result"]={
                "name":tool_result.name,
                "ok":tool_result.ok,
                "result":tool_result.result,
                "error":tool_result.error
            }
            envelope.add_history(
                "system",
                "Результат инструмента "+tool_result.name+": "+str(tool_result.result),
                producer="tool:"+tool_result.name
            )

        response=self.agent.brain.generate(
            BrainRequest(messages=self._messages(envelope))
        )

        envelope.handoff(
            producer=self.agent.brain.brain_id,
            content=response.content,
            metadata={
                "brain_id":response.brain_id,
                "provider":response.provider,
                "model":response.model,
                "metrics":response.metrics,
                "error":response.error
            }
        )

        return {
            "ok":response.error is None,
            "task_id":task_id,
            "agent_id":self.agent.agent_id,
            "brain_id":response.brain_id,
            "competency_id":self.agent.competency_id,
            "input_source":event.source,
            "knowledge_hits":len(knowledge),
            "knowledge_sources":[x.get("source") for x in knowledge],
            "knowledge_modes":[x.get("retrieval_mode","unknown") for x in knowledge],
            "content":response.content,
            "error":response.error,
            "tool":{
                "name":tool_result.name,
                "ok":tool_result.ok,
                "result":tool_result.result,
                "error":tool_result.error
            } if tool_result else None,
            "envelope":{
                "task_id":envelope.task_id,
                "task_type":envelope.task_type,
                "input_text":envelope.input_text,
                "producer":envelope.producer,
                "history":envelope.history,
                "knowledge":envelope.knowledge,
                "artifacts":envelope.artifacts,
                "metadata":envelope.metadata
            }
        }
