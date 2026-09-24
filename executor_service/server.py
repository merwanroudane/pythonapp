"""Execution API (blueprint §5.6): the Streamlit UI posts jobs here; workers run them.

    PLL_EXECUTOR_TOKEN=... python -m executor_service.server --port 8765 --backend docker

POST /run   {"job": {...}, "limits": {...}}  ->  RunResult JSON
GET  /health                                 ->  {"ok": true, "backend": ...}

Hardening: bearer-token auth (constant-time compare), request-size cap, a concurrency
cap, limits clamped to server-side maxima (clients cannot ask for more), and no user
data logged. Put it behind TLS (a reverse proxy) when it is not on localhost.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.execution import docker_backend, local_backend  # noqa: E402
from app.execution.limits import Limits  # noqa: E402

MAX_BODY_BYTES = 256 * 1024
MAX_LIMITS = Limits(timeout_s=30.0, memory_mb=1024, max_file_mb=32, cpus=1.0, pids=64)
JOB_KEYS = {"code", "mode", "trace", "inputs", "boundary"}


def clamp(requested: dict) -> Limits:
    base = Limits()
    values = {}
    for field, ceiling in MAX_LIMITS.as_dict().items():
        value = requested.get(field, getattr(base, field))
        try:
            values[field] = type(ceiling)(min(max(value, 0), ceiling))
        except (TypeError, ValueError):
            values[field] = getattr(base, field)
    return Limits(**values)


def valid_job(job: object) -> bool:
    return (
        isinstance(job, dict)
        and set(job) == JOB_KEYS
        and isinstance(job["code"], str)
        and job["mode"] in ("script", "notebook")
        and isinstance(job["inputs"], list)
        and all(isinstance(v, str) for v in job["inputs"])
        and isinstance(job["boundary"], str)
    )


def make_handler(backend: str, token: str, slots: threading.BoundedSemaphore):
    runner = {"docker": docker_backend.run, "local": local_backend.run}[backend]

    class Handler(BaseHTTPRequestHandler):
        server_version = "PLLExecutor/1.0"

        def log_message(self, fmt: str, *args) -> None:  # never log request bodies
            sys.stderr.write(f"{self.address_string()} {self.command} {self.path}\n")

        def _reply(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._reply(200, {"ok": True, "backend": backend})
            else:
                self._reply(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path != "/run":
                return self._reply(404, {"error": "not found"})
            supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
            if not token or not hmac.compare_digest(supplied, token):
                return self._reply(401, {"error": "unauthorized"})
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY_BYTES:
                return self._reply(413, {"error": "request too large"})
            try:
                request = json.loads(self.rfile.read(length))
            except ValueError:
                return self._reply(400, {"error": "invalid JSON"})
            job = request.get("job") if isinstance(request, dict) else None
            if not valid_job(job):
                return self._reply(400, {"error": "invalid job"})
            if not slots.acquire(timeout=10):
                return self._reply(503, {"error": "busy, try again"})
            try:
                result = runner(job, clamp(request.get("limits") or {}))
            finally:
                slots.release()
            self._reply(200, result.model_dump())

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--backend", choices=["docker", "local"], default="docker")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    token = os.environ.get("PLL_EXECUTOR_TOKEN", "")
    if not token:
        raise SystemExit("Set PLL_EXECUTOR_TOKEN before starting the execution service.")
    if args.backend == "docker" and not docker_backend.docker_available():
        raise SystemExit("Docker engine is not reachable; start it or use --backend local.")
    handler = make_handler(args.backend, token, threading.BoundedSemaphore(args.workers))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"execution service on http://{args.host}:{args.port} (backend={args.backend})")
    server.serve_forever()


if __name__ == "__main__":
    main()
