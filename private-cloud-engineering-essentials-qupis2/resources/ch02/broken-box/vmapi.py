#!/usr/bin/python3
"""vmapi: a tiny VM inventory API used by the broken-box lab.

Reads /etc/vmapi/vmapi.conf (lines of "key = value", "#" starts a comment):

    bind = 127.0.0.1     address to listen on
    port = 8080          TCP port

Endpoints: GET /healthz and GET /vms. Standard library only.
"""
import json
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CONF = "/etc/vmapi/vmapi.conf"

VMS = [
    {"name": "vm-101", "hypervisor": "hv01", "state": "running"},
    {"name": "vm-102", "hypervisor": "hv01", "state": "stopped"},
    {"name": "vm-201", "hypervisor": "hv02", "state": "running"},
]


def read_conf(path):
    """Return the settings in path as a dict of strings."""
    conf = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            key, _, value = line.partition("=")
            conf[key.strip()] = value.strip()
    return conf


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.reply(200, {"status": "ok"})
        elif self.path == "/vms":
            self.reply(200, VMS)
        else:
            self.reply(404, {"error": "not found"})

    def reply(self, status, payload):
        body = (json.dumps(payload) + "\n").encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)


def stop(signum, frame):
    print("vmapi got signal %d, shutting down" % signum, flush=True)
    sys.exit(0)


def main():
    conf = read_conf(CONF)
    host = conf.get("bind", "127.0.0.1")
    port = int(conf.get("port", "8080"))
    signal.signal(signal.SIGTERM, stop)
    server = ThreadingHTTPServer((host, port), Handler)
    print("vmapi listening on %s:%d" % (host, port), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
