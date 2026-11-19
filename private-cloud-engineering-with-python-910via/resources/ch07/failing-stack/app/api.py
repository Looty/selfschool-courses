"""HTTP front end for the failing-stack lab.

At start-up it connects to the db service ONCE (no retry, on purpose) and
remembers whether that worked. GET /health returns 200 when the db answered
PING at start-up, otherwise 503.

Environment:
  DB_HOST    db host name (default "db")
  DB_PORT    db port (default 7000)
  BIND_ADDR  address to listen on (default 127.0.0.1)
  PORT       port to listen on (default 8080)
"""

import json
import os
import signal
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = int(os.environ.get("DB_PORT", "7000"))
STATE = {"db_ok": False, "db_error": "not checked"}


def check_db() -> None:
    try:
        with socket.create_connection((DB_HOST, DB_PORT), timeout=2) as conn:
            conn.sendall(b"PING\n")
            reply = conn.makefile().readline().strip()
        STATE.update(db_ok=reply == "PONG", db_error="" if reply == "PONG" else reply)
    except OSError as exc:
        STATE.update(db_ok=False, db_error=f"{type(exc).__name__}: {exc}")
    if STATE["db_ok"]:
        print(f"api: db at {DB_HOST}:{DB_PORT} answered PONG", flush=True)
    else:
        print(f"api: db check failed ({STATE['db_error']}); serving 503", flush=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            status = 200 if STATE["db_ok"] else 503
            body = json.dumps(STATE).encode() + b"\n"
        else:
            status, body = 404, b"not found\n"
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"api: {self.address_string()} {fmt % args}", flush=True)


def on_sigterm(signum, frame) -> None:
    print("api: SIGTERM received, shutting down", flush=True)
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, on_sigterm)
    check_db()
    addr = os.environ.get("BIND_ADDR", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer((addr, port), Handler)
    print(f"api: listening on {addr}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
