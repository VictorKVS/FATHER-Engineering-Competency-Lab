from father.contracts.types import BrainRequest, AgentResult, KnowledgeQuery, ToolCall

class AgentChassis:
    def __init__(self,agent_id,brain,knowledge,tools,prompt_slot):
        self.agent_id=agent_id
        self.brain=brain
        self.knowledge=knowledge
        self.tools=tools
        self.prompt_slot=prompt_slot
        self.competency_id=None

    def swap_brain(self,brain):
        old=getattr(self.brain,"brain_id",None)
        self.brain=brain
        return {"old":old,"new":getattr(brain,"brain_id",None)}

    def apply_competency(self,pack,knowledge):
        old=self.competency_id
        self.competency_id=pack.id
        self.prompt_slot.load(pack.system_prompt)
        self.knowledge=knowledge
        return {"old":old,"new":self.competency_id}

    def call_tool(self,name,arguments):
        return self.tools.call(ToolCall(name=name,arguments=arguments))

    def run(self,event):
        kb=self.knowledge.search(KnowledgeQuery(text=str(event.content),top_k=5))
        kb_text="\n\n".join(
            f'[SOURCE: {x.get("source","?")} | MODE: {x.get("retrieval_mode","unknown")}]\n{x.get("text",x)}'
            for x in kb.items
        )

        messages=[]
        if self.prompt_slot.system_prompt:
            messages.append({"role":"system","content":self.prompt_slot.system_prompt})

        if kb_text:
            messages.append({
                "role":"system",
                "content":"Ниже подключенная база знаний для текущего Competency Pack. "
                          "Используй её как источник ответа и не заявляй, что доступа к БЗ нет. "
                          "Не выдумывай отсутствующие сведения.\n\n"+kb_text
            })

        messages.append({"role":"user","content":str(event.content)})
        response=self.brain.generate(BrainRequest(messages=messages))

        return AgentResult(
            ok=response.error is None,
            content=response.content,
            metadata={
                "agent_id":self.agent_id,
                "brain_id":response.brain_id,
                "provider":response.provider,
                "model":response.model,
                "competency_id":self.competency_id,
                "knowledge_hits":len(kb.items),
                "knowledge_sources":[x.get("source") for x in kb.items],
                "knowledge_modes":[x.get("retrieval_mode","unknown") for x in kb.items],
                "metrics":response.metrics,
                "error":response.error
            }
        )
