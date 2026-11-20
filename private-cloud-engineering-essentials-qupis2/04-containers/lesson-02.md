---
id: l11
title: "Lab: networking, limits, Compose and a failing stack"
quiz: quiz-11.yaml
resources: [../resources/ch04/failing-stack/compose.yaml, ../resources/ch04/failing-stack/compose.fixed.yaml, ../resources/ch04/failing-stack/app/Dockerfile, ../resources/ch04/failing-stack/app/api.py, ../resources/ch04/failing-stack/app/worker.py, ../resources/ch04/failing-stack/app/probe.py, ../resources/ch04/failing-stack/db/Dockerfile, ../resources/ch04/failing-stack/db/db.py, ../resources/ch04/failing-stack/SOLUTIONS.md]
sources: [75, 76, 77, 78, 79, 80, 81, 82, 105, 125]
---
After this lab you can find and fix five common container faults in a Compose stack (an OOM kill, a start-up race, a wrong listen address, a lost SIGTERM and a missing variable) using only `docker compose` and `docker inspect`.

## Networking in five facts

1. On the default `bridge` network containers reach each other only by IP; on a user-defined network they also resolve each other by name [75] [76].
2. Docker's embedded DNS server on custom networks is `127.0.0.11` [75].
3. Compose creates one network per project, `<project>_default`, and each service is reachable at its service name [82].
4. `"18080:8080"` maps host port 18080 to container port 8080 on all host addresses; `"127.0.0.1:18080:8080"` keeps it on the host [77] [81].
5. Between services use the container port (`db:7000`); only the host uses the published port [82].

A process in a container must listen on `0.0.0.0`. `127.0.0.1` inside a container is that container's own loopback.

## Compose keys that matter

Keys from the Compose reference [81]; the limits match `docker run` [78], as do restart policies [80]. Compose waits for running, not ready, unless you ask for `service_healthy` [82].

```yaml
mem_limit: 64m               # also cpus, pids_limit
depends_on: [db]             # start order only, does not wait for ready
depends_on:
  db: {condition: service_healthy}   # waits for db's healthcheck
healthcheck:
  test: ["CMD", "..."]       # CMD or CMD-SHELL
restart: on-failure:3        # no (default), always, on-failure[:N], unless-stopped
profiles: ["debug"]          # starts only when that profile is active
stop_grace_period: 10s       # stop signal to SIGKILL, default 10s
```

## The stack

| Service | Role |
|---|---|
| `db` | "database" on port 7000; loads for 4 s before listening |
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
   Exit 1 with a traceback is the app. Exit 137 is 128 + 9, SIGKILL [125] [105]; with `OOMKilled=true` it is the memory limit.
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

## Answers in brief

| # | Symptom | Fix |
|---|---|---|
| 1 | worker exit 1, `KeyError: 'DB_HOST'` | `DB_HOST: db` |
| 2 | worker exit 137, `OOMKilled=true` (256 MiB batch, 64 MiB limit) | `BATCH_MB: "32"`, `mem_limit: 128m` |
| 3 | `/health` 503, db connection refused | db `healthcheck` + `condition: service_healthy` |
| 4 | probe: api refused (`BIND_ADDR` defaults to 127.0.0.1) | `BIND_ADDR: "0.0.0.0"` |
| 5 | db stop 10.6 s, exit 137 (shell-form `ENTRYPOINT`) | `entrypoint: ["python", "/app/db.py"]` |

After the fixes every service stopped in under a second with exit 0.

## Gotchas

- **Short `depends_on` means "started", not "ready".** Use a health check plus `service_healthy`, and still retry in code. [81] [82]
- **Raising the limit alone.** After an OOM kill, size the work, not just the limit. [125]

:::key-takeaways
- Compose gives each project a network where service names resolve through Docker's DNS. [75] [82]
- `depends_on` with `condition: service_healthy` plus a `healthcheck` waits for readiness. [81] [82]
- Exit 1 with a traceback is the app; exit 137 with `OOMKilled=true` is the memory limit. [125]
- An app in a container must listen on `0.0.0.0`; choose the host address when publishing. [77]
:::

:::glossary
- **Published port**: a host port forwarded to a container port so clients outside the container network can connect.
- **Health check**: a command run inside the container on a timer whose exit status marks it healthy or unhealthy.:::
