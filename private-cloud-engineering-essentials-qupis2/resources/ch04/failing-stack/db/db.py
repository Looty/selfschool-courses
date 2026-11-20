"""A tiny line-based TCP "database" for the failing-stack lab.

Protocol, one request per line:
  PING  -> PONG
  JOB   -> JOB <n>   (a counter: the next job number)

It spends LOAD_SECONDS (default 4) "loading data" before it opens its port,
like a real database replaying its log at start-up.
"""

import os
import signal
import socketserver
import sys
import threading
import time

PORT = int(os.environ.get("DB_PORT", "7000"))
LOAD_SECONDS = float(os.environ.get("LOAD_SECONDS", "4"))

_counter = 0
_lock = threading.Lock()


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        global _counter
        for raw in self.rfile:
            cmd = raw.decode().strip().upper()
            if cmd == "PING":
                reply = "PONG"
            elif cmd == "JOB":
                with _lock:
                    _counter += 1
                    reply = f"JOB {_counter}"
            else:
                reply = "ERR unknown command"
            self.wfile.write((reply + "\n").encode())


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def on_sigterm(signum, frame) -> None:
    print("db: SIGTERM received, shutting down", flush=True)
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, on_sigterm)
    print(f"db: loading data for {LOAD_SECONDS:g}s", flush=True)
    time.sleep(LOAD_SECONDS)
    with Server(("0.0.0.0", PORT), Handler) as server:
        print(f"db: ready on port {PORT}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
