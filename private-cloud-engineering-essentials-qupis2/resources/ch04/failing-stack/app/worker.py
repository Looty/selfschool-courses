"""Background worker for the failing-stack lab.

Every INTERVAL seconds it asks the db for a job number, then "processes" a
batch by holding BATCH_MB mebibytes in memory for a moment.

Environment:
  DB_HOST   db host name (required: there is no default)
  DB_PORT   db port (default 7000)
  BATCH_MB  size of one batch in MiB (default 16)
  INTERVAL  seconds between batches (default 2)
"""

import os
import signal
import socket
import sys
import time

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", "7000"))
BATCH_MB = int(os.environ.get("BATCH_MB", "16"))
INTERVAL = float(os.environ.get("INTERVAL", "2"))


def next_job() -> str:
    with socket.create_connection((DB_HOST, DB_PORT), timeout=2) as conn:
        conn.sendall(b"JOB\n")
        return conn.makefile().readline().strip()


def process(job: str) -> None:
    # Multiplying a bytearray writes every byte, so the pages are really used.
    batch = bytearray(b"\x01") * (BATCH_MB * 1024 * 1024)
    print(f"worker: {job} processed {len(batch) // (1024 * 1024)} MiB", flush=True)


def on_sigterm(signum, frame) -> None:
    print("worker: SIGTERM received, shutting down", flush=True)
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, on_sigterm)
    print(f"worker: db={DB_HOST}:{DB_PORT} batch={BATCH_MB} MiB", flush=True)
    while True:
        try:
            process(next_job())
        except OSError as exc:
            print(f"worker: db unavailable ({exc}); retrying", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
