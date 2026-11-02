"""Scenario 3: a file descriptor leak. Each 'health check' opens a connection and never closes it."""
import socket
import threading
import time

PORT = 9099
held = []  # the leak: references are kept, so nothing is ever closed


def server() -> None:
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", PORT))
    srv.listen(1024)
    while True:
        try:
            conn, _ = srv.accept()
            held.append(conn)
        except OSError as exc:
            print(f"accept failed: {exc}", flush=True)
            time.sleep(1)


def health_check() -> None:
    s = socket.create_connection(("127.0.0.1", PORT))
    held.append(s)


def main() -> None:
    threading.Thread(target=server, daemon=True).start()
    time.sleep(0.5)
    n = 0
    while True:
        try:
            health_check()
            n += 1
            if n % 50 == 0:
                print(f"{n} health checks done", flush=True)
        except OSError as exc:
            print(f"health check failed after {n}: {exc}", flush=True)
            time.sleep(2)
        time.sleep(0.02)


if __name__ == "__main__":
    main()
