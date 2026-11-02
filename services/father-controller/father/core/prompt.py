class PromptSlot:
    def __init__(self,system_prompt=""): self.system_prompt=system_prompt
    def load(self,system_prompt):
        old=self.system_prompt; self.system_prompt=system_prompt
        return {"old":old,"new":system_prompt}
