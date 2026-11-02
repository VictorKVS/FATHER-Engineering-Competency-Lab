from father.contracts.types import InputEvent
class ApiInputAdapter:
    def normalize(self,payload):
        return InputEvent(source="api",type=payload.get("type","message"),
                          content=payload.get("content",""),metadata=payload.get("metadata",{}))
