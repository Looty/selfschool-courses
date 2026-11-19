---
id: l24
title: "Lab: a VM request API with a job queue"
quiz: quiz-04.yaml
resources: [../resources/ch08/vmapi/app.py, ../resources/ch08/vmapi/tasks.py, ../resources/ch08/vmapi/fakes.py, ../resources/ch08/vmapi/test_api.py, ../resources/ch08/vmapi/app_fastapi.py, ../resources/ch08/vmapi/test_api_fastapi.py, ../resources/ch08/vmapi/requirements.txt, ../resources/ch08/vmapi/Dockerfile, ../resources/ch08/vmapi/compose.yaml, ../resources/ch08/vmapi/smoke.sh]
sources: [46, 50, 51, 52, 56, 58]
---
After this lab you can run a Flask API, an RQ worker and Redis together with Compose, follow one VM request from `POST` to `active`, break the worker in the middle of a job and explain why the VM still ends up right.

## Shortcut

Put the ten files in one folder called `vmapi`, then:

```bash
cd vmapi
python -m venv ../.venv-vmapi && . ../.venv-vmapi/bin/activate   # Windows: ..\.venv-vmapi\Scripts\activate
pip install -r requirements.txt
python -m unittest test_api test_api_fastapi                     # no Redis needed
docker compose up -d --build --wait
bash smoke.sh                                                    # Flask API on 127.0.0.1:8808
bash smoke.sh http://127.0.0.1:8809                              # FastAPI API
docker compose down -v --rmi local
```

In the course's test run the unit tests printed `Ran 21 tests` and `OK` on Python 3.13 and on 3.11, and the stack (Compose project `pce-ch08`) passed every smoke step on Docker 29.9.1. Tested versions: Flask 3.1.3, FastAPI 0.165.0, pydantic 2.14.3, RQ 3.0.0, redis-py 8.1.0, Gunicorn 27.0.1, Uvicorn 0.54.0, httpx 0.28.1, image `python:3.13-slim`, and `redis:8-alpine`, which reported Redis 8.10.3.

## What is in the folder

| File | Role |
| --- | --- |
| `app.py` | Flask factory and blueprint: `POST /vms`, `GET /vms/<id>`, `DELETE /vms/<id>`, `GET /healthz` |
| `tasks.py` | the job `provision(vm_id)`, the status transitions and the Redis lock |
| `fakes.py` | in-memory `FakeRedis` and `FakeQueue` for unit tests |
| `test_api.py`, `test_api_fastapi.py` | 14 and 7 unit tests |
| `app_fastapi.py` | the same API in FastAPI, with plain `def` handlers |
| `requirements.txt`, `Dockerfile` | pinned versions; one image for API and worker |
| `compose.yaml` | `redis` with a healthcheck and AOF on, `api` (Gunicorn), `api-fastapi` (Uvicorn), `worker` |
| `smoke.sh` | create, poll, delete twice, idempotency key, bad input, a failing build |

## Step 1: one request, end to end

`POST /vms` validates the body, writes a Redis hash `vm:<id>` with `status=requested`, enqueues `tasks.provision(vm_id)` and answers `202` with a `Location: /vms/<id>` header. 202 is right because the work is accepted but not done [52]; 201 would claim the VM exists. The job argument is only the id, the minimal data a worker needs [46].

The worker runs `provision`, which moves the status `requested -> building -> active`. If the build raises, `record_failure` counts the attempt and RQ retries after 2 and then 4 seconds; the third failure sets `error` [50]. `DELETE` sets `deleted` from any state and puts a one-hour `EXPIRE` on the hash, so it answers 204 every time and Redis cleans up later [51].

Why not call the hypervisor inside the request? Because a build that takes minutes would hold a Gunicorn worker (a sync worker serves one request at a time [56]), the client would time out, and its retry of a non-idempotent POST could start a second build. The queue turns that into a fast write and a background job.

## Step 2: unit tests without Redis

`create_app(vm_redis, vm_queue)` accepts fakes, so `test_api.py` checks routes and the job logic in milliseconds: one job per POST, 400 for eight bad bodies, the job is idempotent, a VM left in `building` is resumed, three failures end in `error`, and a repeated `Idempotency-Key` returns the first VM. `run_provision(r, vm_id, build_seconds)` holds the logic with the connection passed in, which is what makes it testable; `provision(vm_id)` is the thin wrapper RQ calls.

## Step 3: the stack

`compose.yaml` starts Redis with `--appendonly yes`, which logs every write so a restarted Redis loses at most about the last second [51]; see the Gotchas for the volume this needs. The API and worker wait for Redis to be healthy. The worker runs `rq worker --with-scheduler ... vms`, because retry intervals need the scheduler [50]. It runs in Linux inside Docker, which matters on a Windows laptop, since RQ's default worker forks [50]. The smoke run against the Flask API printed:

```text
== 1. create a VM
  HTTP 202  {"attempts":0,"cpus":2,"id":"1ef80d80adb0","memory_mb":2048,"name":"web-1","status":"requested"}
== 2. poll until active
  14:23:14 status=building attempts=0
  14:23:17 status=active attempts=0
  final: {"attempts":0,"cpus":2,"id":"1ef80d80adb0","memory_mb":2048,"name":"web-1","status":"active"}
== 3. delete it twice
  DELETE -> HTTP 204
  DELETE -> HTTP 204
  GET after delete -> HTTP 404
== 4. same Idempotency-Key twice
  {"attempts":0,"cpus":4,"id":"74b32a1caafc","memory_mb":8192,"name":"db-1","status":"requested"}
  {"attempts":0,"cpus":4,"id":"74b32a1caafc","memory_mb":8192,"name":"db-1","status":"building"}
== 5. an invalid request
  HTTP 400  {"detail":"cpus must be between 1 and 64","error":"Bad Request"}
== 6. a VM whose build always fails (3 attempts, retries after 2 s and 4 s)
  14:23:21 status=building attempts=0
  14:23:23 status=building attempts=1
  14:23:28 status=building attempts=2
  14:23:35 status=error attempts=3
  final: {"attempts":3,"cpus":1,"error":"simulated hypervisor error","id":"b63a9ef17d51","memory_mb":512,"name":"broken-1","status":"error"}
```

(Polling lines in steps 2 and 6 are shortened.) Against the FastAPI service, step 5 gave `HTTP 422` with `"loc":["body","cpus"]` instead of the hand-written 400. Look inside Redis with `docker compose exec redis redis-cli TYPE vm:<id>` (`hash`) and `TTL vm:<id>` (about 3600 after a delete).

## Step 4: kill the worker in the middle of a job

```bash
id=$(curl -s -X POST localhost:8808/vms -H 'Content-Type: application/json' \
  -d '{"name":"victim-1","cpus":1,"memory_mb":512}' | sed -E 's/.*"id":"([^"]+)".*/\1/')
sleep 1.5; docker compose kill -s SIGKILL worker
sleep 90;  curl -s localhost:8808/vms/$id; echo
docker compose start worker; sleep 8; curl -s localhost:8808/vms/$id; echo
```

The course's test run (other fields of the JSON cut):

```text
14:23:42 before kill:      {"attempts":0, ..., "name":"victim-1","status":"building"}
14:25:13 after 90 s:       {"attempts":0, ..., "name":"victim-1","status":"building"}
14:25:23 8 s after start:  {"attempts":0, ..., "name":"victim-1","status":"active"}
```

The worker log showed `cleaning registries for queue: vms`, then the same job id running again and `Job OK`. A `SIGKILL` gives the worker no chance to mark the job failed; RQ's documentation says such an abandoned job is collected by a later worker's cleanup [50]. The VM still finished because the job is idempotent: finding `building`, it simply builds again.

:::low-confidence
Two points come from this one run, not from the documentation. RQ's docs say an abandoned job ends up in `FailedJobRegistry` with `AbandonedJobError` [50]; here, with retries left, it was run again and its final status was `finished`, not `failed`. And when the worker was restarted only a few seconds after the kill, the job stayed `started` and was not picked up until a later restart; the wait seems to depend on the job timeout and the worker's maintenance interval (600 s by default [50]). Check the RQ version you run before relying on either behaviour.
:::

Without the idempotent check, the second run could create a second domain on a real hypervisor. With it, the worst case is a VM stuck in `building` until a cleanup or a reconciliation pass (chapter 9) notices.

## Where the lock is needed

Three writers can touch one VM: the API's DELETE, the worker's start, and the worker's failure handler. Each does "read status, decide, write status". Without a lock, DELETE could read `building`, a worker could then write `active`, and DELETE would overwrite it with `deleted` while the domain keeps running, or the reverse. `tasks.transition` and `record_failure` take `lock:vm:<id>` with `SET NX EX` and a random token and release it with the compare-and-delete script [51]. The idempotency key uses `SET idem:<key> <id> NX EX 86400` the same way, so two concurrent POSTs with one key cannot both create a VM [51].

## Polling and its alternatives

Clients poll `GET /vms/<id>`, which RFC 9110 suggests for 202 by pointing to a status monitor [52]. The common alternatives are a webhook (the service calls the client's URL when done) and Server-Sent Events (the client keeps one connection open for updates). RQ 2.10 added webhooks on jobs [50]. Polling is the simplest to build and to debug.

## Gotchas

- **Pickling Redis clients into jobs.** Pass the id and connect inside the job; arguments are serialised. [46] [50]
- **Simplified Idempotency-Key.** `app.py` returns the first VM even if the second body differs; the draft says that should be 422. Store a hash of the body to do it properly. [58]
- **One Redis client for everything.** The app reads hashes with `decode_responses=True` to get `str`; RQ needs a client without it. In the course's test run, `Job.fetch` on a decoding client raised `UnicodeDecodeError` right after a successful enqueue. Keep two clients, as `create_app` does.
- **Worker without `--with-scheduler`.** Retries with intervals then never run. [50]
- **AOF without a named volume.** `--appendonly yes` logs every write, but this file mounts no named volume: in the course's test run a VM created before `docker compose down` was gone after `up`. Add a named volume for `/data` when the data must outlive the containers.
- **Stuck `building`.** A dead worker leaves the record mid-way; the job must resume it, and something must notice it.

:::key-takeaways
- POST writes a record, enqueues the id, answers 202 with `Location`; a worker does the build. [52] [46]
- Status moves `requested -> building -> active` or `error`; DELETE sets `deleted` and an expiry. [51]
- Retries with intervals need `rq worker --with-scheduler`; the job must survive running twice. [50]
- Read-decide-write on shared state needs a lock; `SET NX EX` with a token is the simple one. [51]
- Killing the worker mid-job left the VM `building` until a worker cleaned up and re-ran the idempotent job.
:::

:::glossary
- **Compose project**: the group of containers, networks and volumes that one `compose.yaml` starts, named here `pce-ch08`.
- **Healthcheck**: a command a container runtime runs repeatedly to decide whether a service is ready.
- **Fake**: a small in-memory object that behaves like a real dependency in tests.
- **Status transition**: a change of a record's status that is allowed only from certain earlier states.
- **Reconciliation pass**: a periodic job that compares recorded state with reality and fixes differences.
- **Webhook**: an HTTP call a service makes to a client's URL when something happens.
- **Server-Sent Events**: a way for a server to push a stream of updates over one open HTTP response.
:::
