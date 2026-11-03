from datetime import datetime, timezone
from father.contracts.types import ToolCall, ToolResult

class ToolRegistry:
    def __init__(self): self._tools={}
    def register(self,name,fn,description=""): self._tools[name]={"fn":fn,"description":description}
    def list(self): return [{"name":k,"description":v["description"]} for k,v in sorted(self._tools.items())]
    def call(self,call):
        if call.name not in self._tools: return ToolResult(name=call.name,ok=False,error="tool_not_found")
        try: return ToolResult(name=call.name,ok=True,result=self._tools[call.name]["fn"](**call.arguments))
        except Exception as e: return ToolResult(name=call.name,ok=False,error=str(e))

def default_tools():
    t=ToolRegistry()
    t.register("echo",lambda text="":text,"Return text unchanged")
    t.register("calculator",lambda a=0,b=0,op="+":a+b if op=="+" else a-b if op=="-" else a*b if op=="*" else a/b if op=="/" else None,"Basic arithmetic")
    t.register("get_time",lambda:datetime.now(timezone.utc).isoformat(),"Return current UTC time")
    return t
