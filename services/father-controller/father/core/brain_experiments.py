import time
from statistics import mean
from father.contracts.types import BrainRequest, KnowledgeQuery
from father.core.context_bus import ContextEnvelope
from father.core.scoring import score_response

class BrainExperimentRunner:
    def __init__(self,assembler,agent,top_k=5):
        self.assembler=assembler
        self.agent=agent
        self.top_k=top_k

    def _prepare_messages(self,event,task_type):
        envelope=ContextEnvelope(
            task_id="brain-experiment",
            task_type=task_type,
            input_text=str(event.content),
            metadata={
                "input_source":event.source,
                "input_type":event.type,
                "input_metadata":event.metadata
            }
        )
        knowledge=self.agent.knowledge.search(
            KnowledgeQuery(text=envelope.input_text,top_k=self.top_k)
        ).items
        envelope.add_knowledge(knowledge)

        messages=[]
        if self.agent.prompt_slot.system_prompt:
            messages.append({
                "role":"system",
                "content":self.agent.prompt_slot.system_prompt
            })

        if knowledge:
            kb_text="\n\n".join(
                f'[SOURCE: {x.get("source","?")} | MODE: {x.get("retrieval_mode","unknown")} | SCORE: {x.get("score",0)}]\n{x.get("text","")}'
                for x in knowledge
            )
            messages.append({
                "role":"system",
                "content":"Контекст RAG/Knowledge для эксперимента. "
                          "Используй его как источник, не выдумывай отсутствующие сведения.\n\n"+kb_text
            })

        messages.append({"role":"user","content":envelope.input_text})
        return messages,knowledge

    def run_case(self,event,task_type,rubric,brain_ids):
        messages,knowledge=self._prepare_messages(event,task_type)
        original=self.agent.brain
        rows=[]

        try:
            for brain_id in brain_ids:
                brain=self.assembler.brain(brain_id)
                self.agent.swap_brain(brain)

                started=time.perf_counter()
                response=brain.generate(BrainRequest(messages=messages))
                latency_ms=round((time.perf_counter()-started)*1000,2)

                quality=score_response(response.content or "",rubric)
                rows.append({
                    "brain_id":brain_id,
                    "provider":response.provider,
                    "model":response.model,
                    "ok":response.error is None,
                    "error":response.error,
                    "latency_ms":latency_ms,
                    "quality":quality,
                    "content":response.content,
                    "knowledge_hits":len(knowledge),
                    "knowledge_sources":[x.get("source") for x in knowledge],
                    "knowledge_modes":[x.get("retrieval_mode","unknown") for x in knowledge]
                })
        finally:
            self.agent.swap_brain(original)

        rows.sort(key=lambda x:(
            0 if x["ok"] else 1,
            0 if x["quality"]["passed"] else 1,
            -float(x["quality"]["score"]),
            float(x["latency_ms"])
        ))

        for rank,row in enumerate(rows,1):
            row["rank"]=rank

        return {
            "winner":rows[0]["brain_id"] if rows else None,
            "results":rows,
            "frozen_context":{
                "messages":messages,
                "knowledge_hits":len(knowledge),
                "knowledge_sources":[x.get("source") for x in knowledge],
                "knowledge_modes":[x.get("retrieval_mode","unknown") for x in knowledge]
            }
        }

    @staticmethod
    def aggregate(cases):
        by_brain={}
        for case in cases:
            for row in case["results"]:
                x=by_brain.setdefault(row["brain_id"],{
                    "brain_id":row["brain_id"],
                    "runs":0,
                    "passed":0,
                    "quality_scores":[],
                    "latencies_ms":[],
                    "errors":0
                })
                x["runs"]+=1
                x["passed"]+=1 if row["quality"]["passed"] else 0
                x["errors"]+=0 if row["ok"] else 1
                x["quality_scores"].append(float(row["quality"]["score"]))
                x["latencies_ms"].append(float(row["latency_ms"]))

        summary=[]
        for x in by_brain.values():
            summary.append({
                "brain_id":x["brain_id"],
                "runs":x["runs"],
                "passed":x["passed"],
                "pass_rate":round(x["passed"]/x["runs"],4) if x["runs"] else 0,
                "avg_quality":round(mean(x["quality_scores"]),2) if x["quality_scores"] else 0,
                "avg_latency_ms":round(mean(x["latencies_ms"]),2) if x["latencies_ms"] else 0,
                "errors":x["errors"]
            })

        summary.sort(key=lambda x:(
            x["errors"],
            -x["pass_rate"],
            -x["avg_quality"],
            x["avg_latency_ms"]
        ))

        for rank,row in enumerate(summary,1):
            row["rank"]=rank

        return {
            "winner":summary[0]["brain_id"] if summary else None,
            "ranking":summary
        }
