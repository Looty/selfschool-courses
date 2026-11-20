"""A tiny HTTP service used to demonstrate Dockerfiles in chapter 7.

Endpoints:
  GET /         -> JSON greeting with the hostname and app version
  GET /health   -> 200 "ok" (used by HEALTHCHECK)
  GET /metrics  -> Prometheus text format (needs prometheus-client)

Configuration comes from the environment:
  PORT         port to listen on (default 8000)
  BIND_ADDR    address to bind (default 0.0.0.0, so a published port works)
  APP_VERSION  version string shown on / (default "dev")

It installs a SIGTERM handler, so `docker stop` ends it at once when it runs
as PID 1 (exec-form ENTRYPOINT) instead of waiting for the SIGKILL.
"""

import json
import os
import signal
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

REQUESTS = Counter("pce_requests_total", "HTTP requests served", ["path"])


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        REQUESTS.labels(path=self.path).inc()
        if self.path == "/health":
            self._send(200, b"ok\n", "text/plain")
        elif self.path == "/metrics":
            self._send(200, generate_latest(), CONTENT_TYPE_LATEST)
        elif self.path == "/":
            body = {
                "service": "pce-ch07-service",
                "host": socket.gethostname(),
                "version": os.environ.get("APP_VERSION", "dev"),
                "pid": os.getpid(),
            }
            self._send(200, (json.dumps(body) + "\n").encode(), "application/json")
        else:
            self._send(404, b"not found\n", "text/plain")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def on_sigterm(signum, frame) -> None:
    print("SIGTERM received, shutting down", flush=True)
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, on_sigterm)
    addr = os.environ.get("BIND_ADDR", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((addr, port), Handler)
    print(f"listening on {addr}:{port} as pid {os.getpid()}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
