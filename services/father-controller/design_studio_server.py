import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from father.core.agent_zoo import AgentZoo
from father.core.block_registry import BlockRegistry
from father.core.design_studio import DesignStudioProject
from father.core.auto_assembly import AutoAssemblyPlanner

BASE=Path(__file__).resolve().parent
WEB=BASE/"design_studio_web"

agents=AgentZoo(
    BASE/"config/agent_zoo.json",
    BASE/"config/contracts/agent_contract_v1.json",
    base_dir=BASE
)
blocks=BlockRegistry(
    BASE/"config/blocks.json",
    BASE/"config/contracts/block_contract_v1.json"
)
planner=AutoAssemblyPlanner(BASE)

MIME={
    ".html":"text/html; charset=utf-8",
    ".css":"text/css; charset=utf-8",
    ".js":"application/javascript; charset=utf-8",
    ".json":"application/json; charset=utf-8",
    ".svg":"image/svg+xml"
}

def catalog():
    return {
        "agents":agents.list(),
        "blocks":blocks.list(),
        "agent_health":agents.validate(),
        "block_health":blocks.health()
    }

class Handler(BaseHTTPRequestHandler):
    def _send(self,status,body,content_type="application/json; charset=utf-8"):
        if isinstance(body,(dict,list)):
            payload=json.dumps(body,ensure_ascii=False,indent=2).encode("utf-8")
        elif isinstance(body,str):
            payload=body.encode("utf-8")
        else:
            payload=body
        self.send_response(status)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(payload)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _json_body(self):
        size=int(self.headers.get("Content-Length","0") or 0)
        raw=self.rfile.read(size) if size else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health":
            return self._send(200,{"status":"ok","service":"father-design-studio","version":"0.1"})
        if path=="/api/catalog":
            return self._send(200,catalog())
        if path=="/api/project/reference":
            project=DesignStudioProject.load(BASE,"config/design_projects/father_general_design.json")
            return self._send(200,project.project)

        if path=="/":
            path="/index.html"
        target=(WEB/path.lstrip("/")).resolve()
        if WEB.resolve() not in target.parents and target!=WEB.resolve():
            return self._send(403,{"error":"forbidden"})
        if not target.exists() or not target.is_file():
            return self._send(404,{"error":"not_found","path":path})
        return self._send(200,target.read_bytes(),MIME.get(target.suffix,"application/octet-stream"))

    def do_POST(self):
        path=urlparse(self.path).path
        try:
            data=self._json_body()
            if path=="/api/validate-design":
                p=DesignStudioProject(BASE,data)
                result=p.validate()
                if result["ok"]:
                    result["product_spec"]=p.export_product_spec()
                return self._send(200,result)
            if path=="/api/auto-assemble":
                return self._send(200,planner.plan(data))
            return self._send(404,{"error":"not_found"})
        except Exception as e:
            return self._send(400,{"error":type(e).__name__,"message":str(e)})

    def log_message(self,fmt,*args):
        print("[DESIGN-STUDIO]",fmt%args)

if __name__=="__main__":
    host="127.0.0.1"
    port=8090
    print(f"FATHER Design Studio: http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()
