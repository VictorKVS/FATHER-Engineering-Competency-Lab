class FailingModel:
    name = "failing-primary"
    def health(self): return False
    def generate(self, prompt, evidence):
        raise RuntimeError("unhealthy primary must never be selected")

class FallbackModel:
    name = "healthy-fallback"
    def health(self): return True
    def generate(self, prompt, evidence):
        return "fallback:" + str(prompt)
