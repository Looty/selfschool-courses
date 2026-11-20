# Failing stack: solutions

Try the lab first. Each fault below gives the symptom you see, the command that shows the cause, the cause,
and the fix. All output is from the course's test run (Docker Engine 29.9.1 on Docker Desktop, WSL2 kernel
6.6, images built from `python:3.13-slim-bookworm`). Container IP addresses will differ on your machine.

The faults are listed in the order you are likely to meet them. Fault 1 hides fault 2: the worker crashes on
start-up before it allocates any memory, so you only see the OOM kill after fixing the environment.

## First look

```bash
docker compose up -d --build
docker compose ps -a --format 'table {{.Service}}\t{{.Status}}'
```

```text
SERVICE   STATUS
api       Up 12 seconds
db        Up 12 seconds
worker    Exited (1) 12 seconds ago
```

## Fault 1: missing environment variable (worker exits 1)

```bash
docker compose logs worker
```

Shortened: two frames of the traceback are left out here.

```text
worker-1  | Traceback (most recent call last):
worker-1  |   File "/app/worker.py", line 19, in <module>
worker-1  |     DB_HOST = os.environ["DB_HOST"]
worker-1  | KeyError: 'DB_HOST'
```

Cause: `worker.py` reads `DB_HOST` with no default and the `worker` service does not set it. Exit status 1 is
Python's status for an uncaught exception, so this is an application error, not a kill.

Fix: add `DB_HOST: db` under the worker's `environment:`.

## Fault 2: OOM kill (worker exits 137)

After fault 1 is fixed, `docker compose up -d` again:

```text
SERVICE   STATUS
api       Up 10 seconds
db        Up 10 seconds
worker    Exited (137) 6 seconds ago
```

```bash
docker compose logs worker
docker inspect -f 'exit={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' pce-ch07-stack-worker-1
```

```text
worker-1  | worker: db=db:7000 batch=256 MiB
worker-1  | worker: db unavailable ([Errno 111] Connection refused); retrying
worker-1  | worker: db unavailable ([Errno 111] Connection refused); retrying
exit=137 OOMKilled=true
```

Cause: each batch holds `BATCH_MB=256` MiB but `mem_limit: 64m` caps the container's cgroup. The kernel's OOM
killer sends SIGKILL (signal 9), and 128 + 9 = 137. There is no Python traceback because SIGKILL cannot be
caught. The two "retrying" lines also show fault 3's cause from the worker's side: the db was not ready yet.

Fix: make the work fit the limit, with headroom for the interpreter: `BATCH_MB: "32"` and `mem_limit: 128m`.
Raising the limit alone hides a sizing bug; decide what one batch should cost first.

## Fault 3: started before ready (api health stays 503)

Ask the api from inside its own container (fault 4 blocks every other route), then read its log:

```bash
docker compose exec api python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/health')"
docker compose logs api
```

```text
urllib.error.HTTPError: HTTP Error 503: Service Unavailable
api-1  | api: db check failed (ConnectionRefusedError: [Errno 111] Connection refused); serving 503
api-1  | api: listening on 127.0.0.1:8080
```

Cause: `depends_on: [db]` (short syntax) only waits until the db container is running. `db.py` spends four
seconds "loading data" before it opens port 7000, and `api.py` checks the db once at start-up, so it caught
the db before it was listening and never checks again.

Fix: give `db` a `healthcheck` that connects to port 7000, and use the long syntax
`depends_on: {db: {condition: service_healthy}}` on `api` and `worker`. In real code also retry the
connection: a dependency can restart at any time, not only at start-up.

```text
 Container pce-ch07-stack-db-1 Waiting
 Container pce-ch07-stack-db-1 Healthy
 Container pce-ch07-stack-api-1 Started
```

## Fault 4: listening on 127.0.0.1 (port published, nothing answers)

```bash
curl -sS -m 3 http://localhost:18080/health
docker compose --profile debug run --rm probe
```

```text
curl: (52) Empty reply from server
db   -> 172.20.0.2      7000: port open
api  -> 172.20.0.3      8080: connect failed: [Errno 111] Connection refused
GET http://api:8080/health -> failed: <urlopen error [Errno 111] Connection refused>
```

The curl message depends on your platform (you may see "Connection reset" instead); the probe output is the
reliable evidence. The name `api` resolves, so DNS and the network are fine; the connection is refused, so
nothing listens on the container's network interface. The api log line `listening on 127.0.0.1:8080` says why.

Cause: `api.py` defaults `BIND_ADDR` to `127.0.0.1`. Inside a container that is the container's own loopback,
which neither other containers nor the published port can reach.

Fix: set `BIND_ADDR: "0.0.0.0"` on `api`. Separately, publish as `"127.0.0.1:18080:8080"` if only the host
itself should reach it: a plain `"18080:8080"` listens on every host address.

## Fault 5: shell-form ENTRYPOINT (db ignores SIGTERM)

```bash
docker compose exec db cat /proc/1/cmdline | tr '\0' ' '; echo
time docker compose stop -t 10 db
docker inspect -f '{{.State.ExitCode}}' pce-ch07-stack-db-1
docker compose logs db | tail -2
```

```text
/bin/sh -c python /app/db.py; echo "db: process exited"
137
db-1  | db: loading data for 4s
db-1  | db: ready on port 7000
```

The stop took 10.6 seconds in the test run.

Cause: `db/Dockerfile` uses `ENTRYPOINT python /app/db.py; echo ...`, the shell form. PID 1 is `/bin/sh`, which
does not pass SIGTERM on to Python, so `db.py`'s handler never runs, the stop waits the full ten seconds and
ends with SIGKILL (137). No "SIGTERM received" line appears in the log.

Fix: exec form, so Python is PID 1. `compose.fixed.yaml` overrides it with
`entrypoint: ["python", "/app/db.py"]`; the lasting fix is the same line in `db/Dockerfile`. After the fix:

the stop took 0.65 seconds, the exit status was 0, and the log ends with:

```text
db-1  | db: SIGTERM received, shutting down
```

## The fixed stack

```bash
docker compose -f compose.fixed.yaml up -d --build
docker compose -f compose.fixed.yaml ps -a --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
curl -sS http://localhost:18080/health
docker compose -f compose.fixed.yaml --profile debug run --rm probe
docker compose -f compose.fixed.yaml down -t 10
```

```text
SERVICE   STATUS                    PORTS
api       Up 6 seconds              127.0.0.1:18080->8080/tcp
db        Up 11 seconds (healthy)   7000/tcp
worker    Up 6 seconds
{"db_ok": true, "db_error": ""}
db   -> 172.19.0.2      7000: port open
api  -> 172.19.0.4      8080: port open
GET http://api:8080/health -> 200 {"db_ok": true, "db_error": ""}
```

Stopping the fixed services one by one (worker, api, db) took 692, 746 and 649 ms, each with exit 0 and a
"SIGTERM received" log line; a full `down -t 10` took 1.2 seconds.

`compose.fixed.yaml` also adds restart policies: `unless-stopped` for the long-running db and api, and
`on-failure:3` for the worker so a crash loop gives up after three tries instead of hiding a bug.
