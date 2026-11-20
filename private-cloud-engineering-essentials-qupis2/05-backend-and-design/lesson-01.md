---
id: l12
title: "A Flask API with an RQ job queue"
quiz: quiz-12.yaml
resources: [../resources/ch05/vmapi/app.py, ../resources/ch05/vmapi/tasks.py, ../resources/ch05/vmapi/fakes.py, ../resources/ch05/vmapi/test_api.py, ../resources/ch05/vmapi/app_fastapi.py, ../resources/ch05/vmapi/test_api_fastapi.py, ../resources/ch05/vmapi/requirements.txt, ../resources/ch05/vmapi/Dockerfile, ../resources/ch05/vmapi/compose.yaml, ../resources/ch05/vmapi/smoke.sh]
sources: [45, 46, 50, 51, 52, 58]
---
After this lesson you can pick methods and status codes for a VM API, queue a slow build with RQ, make a job safe to rerun, and run the stack.

## Safe vs idempotent: what a repeat does

**Rule:** *safe* means "only reads"; *idempotent* means "sending it five times leaves the server as sending it once" [52]. Hook: safe = looking at the lift button; idempotent = pressing it again.

```text
start: VM 7 exists with cpus=4
GET    /vms/7               x2 -> nothing changed          safe
PUT    /vms/7 {"cpus": 2}   x2 -> cpus=2, same as once     idempotent
DELETE /vms/7               x2 -> VM 7 gone, same as once  idempotent
POST   /vms {"name": "db"}  x2 -> TWO new VMs              neither
```

| Method | Safe | Idempotent | Auto-resend after a lost reply? [52] |
| --- | --- | --- | --- |
| GET, HEAD, OPTIONS | yes | yes | yes |
| PUT, DELETE | no | yes | yes |
| POST | no | no | only with the draft `Idempotency-Key` header [58] |

**P1.** The reply to `DELETE /vms/7` is lost. May the client resend it? And `POST /vms`?

:::answer
DELETE yes: idempotent. POST no: it may make a second VM, unless it carries an `Idempotency-Key`.
:::

## Status codes: one per outcome

**Rule:** a 2xx code says how far the work got; a 4xx code says what the client got wrong [52].

```text
store holds VM 1, named web-1
GET    /vms/1                 -> 200 OK           here it is
GET    /vms/99                -> 404 Not Found    no such VM
POST   /vms "hello"           -> 400 Bad Request  not JSON
POST   /vms {"name":"web-1"}  -> 409 Conflict     name taken
DELETE /vms/1                 -> 204 No Content   done, empty body
```

| Code | Meaning [52] | VM API use |
| --- | --- | --- |
| 201 Created | the resource exists now | create that builds before replying |
| 202 Accepted | accepted, not finished | `POST /vms` with a queue |
| 409 Conflict | clashes with current state | duplicate name |

**P2.** `POST /vms` saves the request, queues the build and replies at once. 201 or 202?

:::answer
202: the VM does not exist yet.
:::

## The 202 route: enqueue, then a worker builds

**Rule:** the web request only records and enqueues; a separate worker process does the minutes-long build [46].

```python
import uuid
from flask import Flask
from redis import Redis
from rq import Queue, Retry
import tasks                       # provision() lives in a module, not __main__

app = Flask(__name__)
queue = Queue("vms", connection=Redis())

@app.post("/vms")
def create_vm():
    vm_id = uuid.uuid4().hex[:12]
    # first store the record with status "requested"
    job = queue.enqueue(tasks.provision, vm_id,
                        job_id=f"provision-{vm_id}", job_timeout=60,
                        retry=Retry(max=2, interval=[2, 4]))
    return {"id": vm_id, "job": job.id}, 202, {"Location": f"/vms/{vm_id}"}
```

A tuple `(body, status, headers)` sets the code; a dict becomes JSON [45]. Pass only the id [46].

A worker with `--with-scheduler` runs an always-failing job (test run) [50]:

```text
  0.0s job=started    vm=building  attempts=0
  2.4s job=scheduled  vm=building  attempts=1   # waits 2 s
  4.4s job=started    vm=building  attempts=1
  7.5s job=scheduled  vm=building  attempts=2   # waits 4 s
 11.5s job=started    vm=building  attempts=2
 14.5s job=failed     vm=error     attempts=3   # max=2 retries = 3 runs
```

Edge cases [50]: intervals need `--with-scheduler`; `job_timeout` defaults to 180 s, then the job is killed and failed.

**P3.** A job has `retry=Retry(max=4)` and always fails. How many runs?

:::answer
5: one run plus four retries.
:::

## Idempotent jobs and a Redis lock

**Rule:** write the job as "make this VM built", not "build a VM": read the status first. Retries, requeues and `kill -9` can all run it twice [50].

```text
status found   -> what tasks.provision does
requested      -> set building, build, set active
building       -> build again: an earlier run died
active         -> nothing
error, deleted -> nothing
no record      -> nothing
```

A lock stops overlapping runs: `SET ... NX EX` sets only an absent key, with an expiry [51].

```text
SET lock:vm:42 tok-a NX EX 10   -> OK     worker A holds it
SET lock:vm:42 tok-b NX EX 10   -> nil    B must wait
(10 s pass, the key expires)
SET lock:vm:42 tok-b NX EX 10   -> OK     B holds it
A, late: delete if value == tok-a -> 0    B's lock survives
```

Contrast: a plain `DEL` from late A would delete B's lock; compare-and-delete leaves it [51].

**P4.** A worker is killed with `kill -9` mid-build; status stays `building`. The job runs again. What does it do?

:::answer
It builds again: `building` means an earlier run died.
:::

## Lab: run the stack (30 minutes)

1. `cd resources/ch05/vmapi`, make a venv, `pip install -r requirements.txt`.
2. `python -m unittest test_api test_api_fastapi` (no Redis needed): expect `Ran 21 tests`, `OK`.
3. `docker compose up -d --build --wait` starts Redis, the Flask API (Gunicorn), a FastAPI copy and a worker with `--with-scheduler`.
4. `bash smoke.sh`, then `bash smoke.sh http://127.0.0.1:8809` (FastAPI). Watch `requested -> building -> active`, DELETE giving 204 twice, and a failing build ending in `error` after 3 attempts.
5. Start a build, then `docker compose kill -s SIGKILL worker` and later `docker compose start worker`. The VM stays `building` until a worker cleans up and reruns the idempotent job.
6. `docker compose down -v --rmi local`; read `tasks.py` as the solution.

:::low-confidence
Step 5 is from one run. RQ's docs say an abandoned job goes to `FailedJobRegistry` [50]; here, with retries left, it reran. Check your RQ version.
:::

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| idempotent | repeat = once | `DELETE` x2 → gone |
| 202 | accepted, not done | queued create → 202 |
| `Retry(max=n)` | n+1 runs | `max=2` → 3 |
| `SET NX EX` | set if absent | second SET → nil |

## If you missed a quiz question

**If you thought** idempotent means read-only: reread "Safe vs idempotent". **R4.** Is `PUT` safe?

:::answer
No: it changes state.
:::

**If you thought** queued create is 201; duplicate is 400: reread "Status codes". **R1.** Valid JSON, taken name?

:::answer
409: the JSON is fine; the name clashes.
:::

**If you thought** `max=2` is 2 runs; no timeout: reread "The 202 route". **R2.** A 4-minute job?

:::answer
Killed at 180 s, marked failed.
:::

**If you thought** `building` means someone is working; `DEL` releases: reread "Idempotent jobs". **R3.** Why not `DEL`?

:::answer
It deletes B's lock.
:::

:::key-takeaways
- Idempotent: GET, HEAD, OPTIONS, PUT, DELETE; only the first three are safe. 202 means accepted for later. [52]
- RQ: 180 s default timeout; `max=n` gives n+1 runs; jobs read state first. [50]
- Locks: `SET NX EX` plus compare-and-delete. [51]
:::

:::glossary
- **Safe**: a request that changes nothing on the server.
- **Idempotent**: sending it many times has the effect of sending it once.
- **RQ**: a Python library that keeps jobs in Redis and runs them in workers.
- **Worker**: a long-running process that takes jobs from a queue and runs them.
- **Idempotency-Key**: a unique value that lets the server spot a retried request.
:::
