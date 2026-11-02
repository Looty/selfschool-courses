"""Scenario 4: a service that keeps writing to its log file, even after someone deletes it."""
import sys
import time

path = sys.argv[1] if len(sys.argv) > 1 else "/data/app.log"
line = ("x" * 1023 + "\n").encode()

with open(path, "ab", buffering=0) as log:
    while True:
        try:
            for _ in range(1024):  # about 1 MiB per round
                log.write(line)
        except OSError as exc:
            print(f"write failed: {exc}", flush=True)
            time.sleep(2)
        time.sleep(0.05)
