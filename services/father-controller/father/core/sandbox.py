import concurrent.futures

class ExecutionSandbox:
    def __init__(self, timeout_sec=2, max_text_chars=2000, max_abs_number=1000000):
        self.timeout_sec=float(timeout_sec)
        self.max_text_chars=int(max_text_chars)
        self.max_abs_number=float(max_abs_number)

    def validate(self, tool_name, arguments):
        args=arguments or {}

        if tool_name=="calculator":
            allowed={"a","b","op"}
            extra=set(args)-allowed
            if extra:
                return {"allowed":False,"reason":"unexpected_arguments","extra":sorted(extra)}

            op=args.get("op","+")
            if op not in {"+","-","*","/"}:
                return {"allowed":False,"reason":"operator_not_allowed","op":op}

            for key in ("a","b"):
                value=args.get(key,0)
                if not isinstance(value,(int,float)):
                    return {"allowed":False,"reason":"number_required","argument":key}
                if abs(float(value))>self.max_abs_number:
                    return {"allowed":False,"reason":"number_limit","argument":key,"value":value}

            return {"allowed":True,"reason":"validated"}

        if tool_name=="echo":
            allowed={"text"}
            extra=set(args)-allowed
            if extra:
                return {"allowed":False,"reason":"unexpected_arguments","extra":sorted(extra)}
            text=str(args.get("text",""))
            if len(text)>self.max_text_chars:
                return {"allowed":False,"reason":"text_limit","chars":len(text),"max_chars":self.max_text_chars}
            return {"allowed":True,"reason":"validated"}

        return {"allowed":False,"reason":"tool_not_sandboxed","tool_name":tool_name}

    def execute(self, agent, tool_name, arguments):
        decision=self.validate(tool_name,arguments)
        if not decision["allowed"]:
            return {
                "ok":False,
                "blocked":True,
                "reason":decision["reason"],
                "decision":decision,
                "tool_name":tool_name
            }

        pool=concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future=pool.submit(agent.call_tool,tool_name,arguments or {})
        try:
            result=future.result(timeout=self.timeout_sec)
            return {
                "ok":bool(result.ok),
                "blocked":False,
                "reason":"executed" if result.ok else (result.error or "tool_error"),
                "tool_name":result.name,
                "result":result.result,
                "error":result.error,
                "decision":decision
            }
        except concurrent.futures.TimeoutError:
            future.cancel()
            return {
                "ok":False,
                "blocked":True,
                "reason":"timeout",
                "tool_name":tool_name,
                "decision":decision
            }
        finally:
            pool.shutdown(wait=False,cancel_futures=True)

    def health(self):
        return {
            "status":"ok",
            "timeout_sec":self.timeout_sec,
            "max_text_chars":self.max_text_chars,
            "max_abs_number":self.max_abs_number,
            "sandboxed_tools":["calculator","echo"]
        }
