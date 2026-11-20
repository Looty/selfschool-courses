---
id: l11
title: "Lab: networking, limits, Compose and a failing stack"
quiz: quiz-11.yaml
resources: [../resources/ch04/failing-stack/compose.yaml, ../resources/ch04/failing-stack/compose.fixed.yaml, ../resources/ch04/failing-stack/app/Dockerfile, ../resources/ch04/failing-stack/app/api.py, ../resources/ch04/failing-stack/app/worker.py, ../resources/ch04/failing-stack/app/probe.py, ../resources/ch04/failing-stack/db/Dockerfile, ../resources/ch04/failing-stack/db/db.py, ../resources/ch04/failing-stack/SOLUTIONS.md]
sources: [75, 76, 77, 79, 81, 82, 105, 125]
---
After this lab you can publish a port, connect containers by name, wait for readiness, and fix five faults in a Compose stack (Docker Engine 29.9, Docker Desktop).

## `-p host:container`: a door from the host

**Rule:** `-p 18080:8000` forwards host port 18080 to port 8000 *inside* the container, and the app must listen on `0.0.0.0` there to answer [77]. Hook: host on the left, container on the right.

```console
$ docker run -d --name web1 -p 18080:8000 python:3.13-slim-bookworm python -m http.server 8000
$ docker run -d --name web2 -p 18081:8000 python:3.13-slim-bookworm python -m http.server 8000 --bind 127.0.0.1
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/
200                          # host 18080 -> container 8000
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18081/
000                          # no HTTP answer: web2 listens on its own loopback
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/
000                          # edge case: the container port alone is not published
```

With no host address, `-p` listens on every host address; `-p 127.0.0.1:18080:8000` keeps it on the host [77].

**P1.** An app listens on `127.0.0.1:8080` in its container, published with `-p 9000:8080`. What does `curl localhost:9000` on the host get?

:::answer
No HTTP answer: forwarded traffic arrives on the container's interface, where nothing listens.
:::

## Container DNS: names work on a user network

**Rule:** on a user-defined network, containers reach each other by name through Docker's DNS server at `127.0.0.11`; on the default `bridge` network they can use only IPs [75] [76]. Compose makes one such network per project, `<project>_default`, and each service is reachable by its service name [82].

A Python probe tried each `name:port` (its own messages):

```text
# default bridge network
web1:8000        name not found
# user network: docker network create labnet, then connect web1 and web2
web1:8000        open
web1:18080       refused     # 18080 exists only on the host
web2:8000        refused     # resolves, but web2 listens on 127.0.0.1
localhost:8000   refused     # localhost is the probe itself
$ grep nameserver /etc/resolv.conf    # inside a container on labnet
nameserver 127.0.0.11
```

Between services use the container port (`db:7000`); only the host uses the published port [82].

**P2.** In Compose, `worker` connects to `api:18080`, with api's ports set to `"18080:8080"`. Does it work?

:::answer
No. 18080 exists only on the host; inside the network use `api:8080`.
:::

## `depends_on`: started is not ready

**Rule:** short `depends_on` waits until the other container is *running*, not *ready*; to wait for ready, give it a `healthcheck` and use `condition: service_healthy` [81] [82].

```yaml
depends_on: [db]                   # starts api right after db starts
depends_on:
  db: {condition: service_healthy} # waits until db's healthcheck passes
```

The lab's `db` needs 4 s to start listening; `api` checks it once:

| api's `depends_on` | What happened in the test run |
| --- | --- |
| `[db]` | api checked too early: `/health` 503 forever |
| `service_healthy` + db `healthcheck` | Compose printed db `Waiting`, then `Healthy`, then started api: 200 |

Edge case: ready once is not ready forever, so still retry in code [81] [82].

**P3.** db has no `healthcheck` and api uses short `depends_on`. Does api wait 4 s?

:::answer
No: it starts once db's container runs.
:::

## The stack

| Service | Role |
|---|---|
| `db` | "database" on port 7000; 4 s start-up |
| `api` | HTTP on 8080; checks db once at start-up; `/health` is 200 or 503 |
| `worker` | takes a job every 2 s, holds `BATCH_MB` MiB |
| `probe` | profile `debug`; connects to `db:7000` and `api:8080` |

## The lab (40 min)

From `resources/ch04/failing-stack`:

1. `docker compose up -d --build` (project `pce-ch07-stack`).
2. **Status and exit codes.**
   ```bash
   docker compose ps -a
   docker inspect -f 'exit={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' pce-ch07-stack-worker-1
   docker compose logs worker
   ```
   Exit 1 with a traceback is the app. Exit 137 is 128 + 9, SIGKILL [125] [105]; with `OOMKilled=true` it is the memory limit (previous lesson).
3. **Network.** `docker compose --profile debug run --rm probe`. Resolves but refused: nothing listens on that interface.
4. **Readiness.** `docker compose logs api db`: did api check db before db said `ready`?
5. **PID 1.** `docker stop` signals the main process only [79]. Check it:
   ```bash
   docker compose exec db cat /proc/1/cmdline | tr '\0' ' '; echo
   docker compose stop -t 10 db
   ```
   If PID 1 is `/bin/sh -c ...`, the app never got SIGTERM.
6. Fix one fault, run `docker compose up -d`, re-read status: the first fault hides the next.
7. Compare with `docker compose -f compose.fixed.yaml up -d --build`, then `curl -s http://localhost:18080/health` (test run: `{"db_ok": true, "db_error": ""}`). Then read `SOLUTIONS.md`.

## Lab fixes in brief

| # | Symptom | Fix |
|---|---|---|
| 1 | worker exit 1, `KeyError: 'DB_HOST'` | `DB_HOST: db` |
| 2 | worker exit 137, `OOMKilled=true` (256 MiB batch, 64 MiB limit) | `BATCH_MB: "32"`, `mem_limit: 128m` |
| 3 | `/health` 503, db connection refused | db `healthcheck` + `condition: service_healthy` |
| 4 | probe: api refused (`BIND_ADDR` defaults to 127.0.0.1) | `BIND_ADDR: "0.0.0.0"` |
| 5 | db stop 10.6 s, exit 137 (shell-form `ENTRYPOINT`) | `entrypoint: ["python", "/app/db.py"]` |
## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `-p H:C` | host port H → container port C | `-p 18080:8000` → `localhost:18080` |
| listen address | `0.0.0.0` inside the container | `127.0.0.1` → `000` from host |
| user network DNS | names via `127.0.0.11` | `web1:8000` → open |
| `depends_on` | short: running; `service_healthy`: ready | api 503 / 200 |

## If you missed a quiz question

**If you thought** the container port is on the left: reread "`-p`". **R1.** In `-p 18080:8080`, which is the host port?

:::answer
The left one, 18080.
:::

**If you thought** `127.0.0.1` in a container is the host: reread "`-p`". **R2.** Whose loopback is it?

:::answer
Its own loopback.
:::

**If you thought** names resolve on the default bridge: reread "Container DNS". **R3.** Do two containers there reach each other by name?

:::answer
No: only user-defined networks resolve names.
:::

**If you thought** `depends_on` waits for ready: reread "`depends_on`". **R4.** What two things make Compose wait?

:::answer
A `healthcheck` on db and `condition: service_healthy`.
:::

:::key-takeaways
- `-p host:container` needs the app on `0.0.0.0`. [77]
- On user networks names resolve via Docker's DNS; use the container port. [75] [82]
- Only `service_healthy` plus a `healthcheck` waits for readiness. [81] [82]
:::

:::glossary
- **Published port**: a host port forwarded to a container port so clients outside the container network can connect.
- **Loopback**: the 127.0.0.1 address that only reaches the same network namespace it is used from.
- **Embedded DNS**: the resolver Docker runs at 127.0.0.11 that answers container and service names.
- **Health check**: a command run inside the container on a timer whose exit status marks it healthy or unhealthy.
:::
