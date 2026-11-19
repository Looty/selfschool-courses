"""Network probe for the failing-stack lab, run as a one-off debug container.

  docker compose --profile debug run --rm probe

It resolves each service name through Docker's embedded DNS and tries to
connect, so you can tell "name does not resolve" from "nothing listens".
"""

import socket
import urllib.error
import urllib.request

TARGETS = [("db", 7000), ("api", 8080)]


def main() -> None:
    for host, port in TARGETS:
        try:
            addr = socket.gethostbyname(host)
        except OSError as exc:
            print(f"{host:4} DNS failed: {exc}")
            continue
        try:
            socket.create_connection((addr, port), timeout=2).close()
            result = "port open"
        except OSError as exc:
            result = f"connect failed: {exc}"
        print(f"{host:4} -> {addr:15} {port}: {result}")
    try:
        with urllib.request.urlopen("http://api:8080/health", timeout=2) as resp:
            print(f"GET http://api:8080/health -> {resp.status} {resp.read().decode().strip()}")
    except urllib.error.HTTPError as exc:
        print(f"GET http://api:8080/health -> {exc.code} {exc.read().decode().strip()}")
    except OSError as exc:
        print(f"GET http://api:8080/health -> failed: {exc}")


if __name__ == "__main__":
    main()
