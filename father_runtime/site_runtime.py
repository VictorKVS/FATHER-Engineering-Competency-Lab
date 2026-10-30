from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json

from .project_init import ProjectInitializer
from .event_log import FactoryEventLogger


class Handler(BaseHTTPRequestHandler):
    initializer = ProjectInitializer()
    events = FactoryEventLogger()

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed=urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"status": "ok", "service": "father-site-runtime"})
            return
        if parsed.path.startswith("/events/"):
            session_id=parsed.path.split("/events/",1)[1]
            self._json(200, {"session_id":session_id,"events":self.events.read_session(session_id)})
            return
        self._json(404, {"error": "not_found"})

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/events":
                self.events.emit(
                    session_id=payload.get("session_id","unknown"),
                    stage_id=payload.get("stage_id","UI"),
                    source=payload.get("source","UI"),
                    event_type=payload.get("event_type","UI_EVENT"),
                    action=payload.get("action","unknown"),
                    status=payload.get("status","INFO"),
                    project_id=payload.get("project_id"),
                    actor=payload.get("actor","USER"),
                    target=payload.get("target"),
                    details=payload.get("details") or {},
                    parent_event_id=payload.get("parent_event_id"),
                    correlation_id=payload.get("correlation_id"),
                )
                self._json(200, {"status":"logged"})
                return
            if path == "/stage001/preflight":
                result = self.initializer.preflight(payload["proposal"], payload["execution_plan"])
                self._json(200, result.to_dict())
                return
            if path == "/stage001/execute":
                result = self.initializer.execute(
                    payload["proposal"],
                    payload["execution_plan"],
                    approved=bool(payload.get("approved")),
                )
                self._json(200, result)
                return
            if path == "/stage001/verify":
                self._json(200, self.initializer.verify(payload["proposal"]))
                return
            if path == "/open/local":
                self.initializer.open_local(payload["path"])
                self._json(200, {"status": "opened"})
                return
            if path == "/open/github":
                self.initializer.open_github(payload["url"])
                self._json(200, {"status": "opened"})
                return
            self._json(404, {"error": "not_found"})
        except Exception as exc:
            self._json(500, {"error": type(exc).__name__, "message": str(exc)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"FATHER site runtime: http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
