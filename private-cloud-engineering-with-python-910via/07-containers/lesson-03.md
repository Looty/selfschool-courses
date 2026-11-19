---
id: l20
title: "Lab: networking, limits, Compose and a failing stack"
quiz: quiz-03.yaml
resources: [../resources/ch07/failing-stack/compose.yaml, ../resources/ch07/failing-stack/compose.fixed.yaml, ../resources/ch07/failing-stack/app/Dockerfile, ../resources/ch07/failing-stack/app/api.py, ../resources/ch07/failing-stack/app/worker.py, ../resources/ch07/failing-stack/app/probe.py, ../resources/ch07/failing-stack/db/Dockerfile, ../resources/ch07/failing-stack/db/db.py, ../resources/ch07/failing-stack/SOLUTIONS.md]
sources: [75, 76, 77, 78, 79, 80, 81, 82, 105, 125]
---
After this lab you can find and fix five common container faults in a Compose stack (an OOM kill, a start-up race, a wrong listen address, a lost SIGTERM and a missing variable) using only `docker compose` and `docker inspect`.

## Shortcut

Download the `failing-stack` folder, keep its layout, and from inside it:

```bash
docker compose up -d --build                       # the broken stack, project pce-ch07-stack
docker compose ps -a
docker compose --profile debug run --rm probe      # network check from inside the stack
docker compose down
docker compose -f compose.fixed.yaml up -d --build # the reference fix
curl -s http://localhost:18080/health
docker compose -f compose.fixed.yaml down -t 10
```

In the course's test run (Docker Engine 29.9.1, Compose on Docker Desktop) the broken stack showed `worker Exited (1)` and the probe could not connect to `api`; the fixed stack answered `{"db_ok": true, "db_error": ""}`. Full output for every step is in `SOLUTIONS.md`. Read it only after your own attempt.

## Networking in five facts

1. On the default `bridge` network containers reach each other only by IP; on a user-defined network they also resolve each other by name [75] [76].
2. Containers on a custom network use Docker's embedded DNS server at `127.0.0.11` [75].
3. Compose creates one network per Compose project, `<project>_default`, and each service is reachable at its service name [82]. This stack's network is `pce-ch07-stack_default`.
4. `-p 18080:8080` (Compose: `"18080:8080"`) maps host port 18080 to container port 8080. With no host address it listens on all host addresses, which the docs call insecure by default; `"127.0.0.1:18080:8080"` keeps it on the host [77] [81].
5. Inside the network, services use the container port (`db:7000`); only the host uses the published port [82].

A process inside a container must listen on `0.0.0.0` (or the container's address) for any of this to work. `127.0.0.1` inside a container is that container's own loopback.

## Limits, health and restarts in Compose

| Compose key | What it does |
| --- | --- |
| `mem_limit`, `cpus`, `pids_limit` | the `--memory`, `--cpus`, `--pids-limit` limits [81] [78] |
| `depends_on: [db]` | start order only; does not wait for health [81] |
| `depends_on: {db: {condition: service_healthy}}` | wait until db's health check passes [81] [82] |
| `healthcheck.test` | list starting with `CMD` or `CMD-SHELL`; a plain string means `CMD-SHELL` [81] |
| `restart` | `no` (default), `always`, `on-failure[:N]`, `unless-stopped` [81] |
| `profiles` | service starts only when a listed profile is active [81] |
| `stop_grace_period` | wait between the stop signal and SIGKILL, default 10s [81] |

Compose waits until a container is running, not until it is ready, unless you ask for `service_healthy` [82]. Each restart policy also exists on `docker run --restart` [80].

## The stack

| Service | Image | Role |
| --- | --- | --- |
| `db` | `db/Dockerfile` | line-protocol "database" on port 7000; spends 4 s "loading data" before listening |
| `api` | `app/Dockerfile` | HTTP on 8080; checks the db once at start-up; `/health` is 200 or 503 |
| `worker` | `app/Dockerfile` | takes a job from db every 2 s and holds `BATCH_MB` MiB while "processing" |
| `probe` | `app/Dockerfile` | profile `debug`; resolves and connects to `db:7000` and `api:8080` |

Five faults are planted. Symptoms you will meet:

- `worker` exits with status 1, and later, once that is fixed, with status 137.
- `api` stays up but `/health` never turns 200.
- `curl http://localhost:18080/health` from the host gets an empty reply or a reset.
- `docker compose stop -t 10 db` takes ten seconds and leaves no shutdown message.

## Step 1: read status and exit codes

```bash
docker compose ps -a --format 'table {{.Service}}\t{{.Status}}'
docker inspect -f 'exit={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' pce-ch07-stack-worker-1
docker compose logs worker
```

Status 1 with a traceback is the application failing. Status 137 is 128 + 9, SIGKILL [125] [105]; with `OOMKilled=true` it is the memory limit (lesson 1 of this chapter). Fix one fault, run `docker compose up -d` again, and read the status again: the first worker fault hides the second.

## Step 2: check the network from inside

```bash
docker compose --profile debug run --rm probe
```

```text
db   -> 172.20.0.2      7000: port open
api  -> 172.20.0.3      8080: connect failed: [Errno 111] Connection refused
GET http://api:8080/health -> failed: <urlopen error [Errno 111] Connection refused>
```

The name resolved, so DNS and the network work; the connection was refused, so nothing listens on that interface. Read the service's own log line about where it listens.

## Step 3: check readiness and start order

```bash
docker compose logs api db
```

Compare the time the api checked the db with the time the db said `ready`. Then look at the `depends_on` form in `compose.yaml`.

## Step 4: check who is PID 1

```bash
docker compose exec db cat /proc/1/cmdline | tr '\0' ' '; echo
docker compose stop -t 10 db
docker inspect -f '{{.State.ExitCode}}' pce-ch07-stack-db-1
```

`docker stop` signals the main process only [79]. If PID 1 is `/bin/sh -c ...`, the app never got SIGTERM.

## Answers in brief

| # | Symptom | Cause | Fix |
| --- | --- | --- | --- |
| 1 | worker `Exited (1)`, `KeyError: 'DB_HOST'` | variable not set | `DB_HOST: db` |
| 2 | worker `Exited (137)`, `OOMKilled=true` | 256 MiB batch, `mem_limit: 64m` | `BATCH_MB: "32"`, `mem_limit: 128m` |
| 3 | `/health` 503: `db check failed ... Connection refused` | short `depends_on` | db `healthcheck` + `condition: service_healthy` |
| 4 | probe: api connection refused | `BIND_ADDR` defaults to `127.0.0.1` | `BIND_ADDR: "0.0.0.0"` |
| 5 | db stop 10.6 s, exit 137 | shell-form `ENTRYPOINT` | `entrypoint: ["python", "/app/db.py"]` |

After the fixes, stopping worker, api and db took 0.69, 0.75 and 0.65 s, each with exit 0 and a `SIGTERM received` line. Compose printed `Container pce-ch07-stack-db-1 Waiting` then `Healthy` before starting `api`.

## Check yourself

- Set `LOAD_SECONDS: "20"` on db in the fixed file. What does `docker compose up -d` print, and for how long? (The health check retries every 2 s, 15 times.)
- Remove the `127.0.0.1:` prefix from the api port. Who can now reach port 18080?
- Change the worker to `restart: always` with the old 64 MiB limit. What does `docker compose ps` show over a minute, and why is `on-failure:3` kinder to whoever is on call?

## Gotchas

- **Short `depends_on` means "started", not "ready".** Use a health check plus `service_healthy`, and still retry in code. [81] [82]
- **Binding to 127.0.0.1 inside a container.** Published ports and other containers cannot reach it; listen on `0.0.0.0`. [77]
- **Publishing on all host addresses by accident.** `"18080:8080"` is reachable from the network; prefix `127.0.0.1:` for local-only. [77]
- **Reading 137 as a crash.** Check `OOMKilled` first; then size the work, not just the limit. [125]
- **The first error hides the next.** Re-run and re-read status after every fix.
- **Using the published port between services.** Inside the network it is `db:7000`, not `localhost:18080`. [82]

:::low-confidence
The host-side `curl` message depends on the platform: Docker Desktop on Windows gave `curl: (52) Empty reply from server`; a Linux host may print "Connection reset by peer" or "Connection refused". The probe output is the reliable evidence. Container IP addresses differ per run. The stop times above used an explicit `-t 10`; this Docker Desktop install used a shorter default without it (see lesson 2).
:::

:::key-takeaways
- Compose gives each project a network where service names resolve through Docker's DNS. [75] [82]
- `depends_on` with `condition: service_healthy` plus a `healthcheck` is how to wait for readiness. [81] [82]
- Exit 1 with a traceback is the app; exit 137 with `OOMKilled=true` is the memory limit. [125]
- An app in a container must listen on `0.0.0.0`; choose the host address when publishing. [77]
- Exec-form entrypoints let `docker stop` end a service in under a second. [79]
:::

:::glossary
- **Compose project**: one running copy of a Compose application, whose name prefixes its containers and network.
- **Service**: one entry under `services:` in a Compose file, run as one or more identical containers.
- **Embedded DNS**: the resolver Docker runs at 127.0.0.11 that answers container and service names.
- **Published port**: a host port forwarded to a container port so clients outside the container network can connect.
- **Health check**: a command run inside the container on a timer whose exit status marks it healthy or unhealthy.
- **Restart policy**: the rule that decides whether Docker starts a container again after it exits.
- **Profile**: a label that keeps a Compose service switched off until you ask for it.
- **Loopback**: the 127.0.0.1 address that only reaches the same network namespace it is used from.
:::
