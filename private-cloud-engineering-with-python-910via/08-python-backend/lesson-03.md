---
id: l23
title: "RQ and Redis: jobs, workers and retries"
quiz: quiz-03.yaml
sources: [46, 50, 51, 52, 58, 59]
---
After this lesson you can put slow work on an RQ queue with the right timeouts and retries, explain what a worker does with each job, write a job that is safe to run twice, and use Redis keys, expiry and a simple lock correctly.

## Why a queue at all

Creating a VM takes minutes. If the web request waits, the client times out, a web worker is tied up, and a retry may start a second build. The Flask docs give the pattern: send the work to another process through a task queue and return immediately; a second route reports the result, so request workers are never blocked [46]. Pass the minimum the job needs, such as an id, not whole objects, because arguments are serialised to cross processes [46]. The HTTP side is `202 Accepted`, whose body ought to describe the current status and point to where it can be monitored [52].

A queue in Redis also outlives the API process, lets you add workers without touching the API, and gives failed work a place to wait for a retry.

## RQ in five names

RQ is a Python library that queues jobs in Redis (or Valkey, the other server it names as a supported backend) and runs them in worker processes [50]. Version 3.0.0 was released on 2026-10-28, needs Python 3.10 or later, and supports Redis 5 or later or Valkey 7.2 or later [50]. The course's test run used RQ 3.0.0, redis-py 8.1.0 and the `redis:8-alpine` image, which reported Redis 8.10.3.

| Name | What it is [50] |
| --- | --- |
| `Queue` | an ordered list of jobs, first in, first out |
| `Job` | the function to call and its arguments |
| `Worker` | a process that takes jobs from queues and runs them |
| `Execution` | runtime data for one run of a job |
| `Result` | the outcome of one execution, success or failure |

```python
from redis import Redis
from rq import Queue, Retry

q = Queue("vms", connection=Redis())
job = q.enqueue(provision, vm_id,
                job_id=f"provision-{vm_id}",
                job_timeout=60,
                retry=Retry(max=2, interval=[2, 4]))
```

| `enqueue` option | Meaning and default [50] |
| --- | --- |
| `job_timeout` | maximum run time before the job is killed and marked failed; default 180 s |
| `result_ttl` | how long a successful job and its result are kept; default 500 s (`-1` never expires) |
| `ttl` | how long a job may wait in the queue before it is discarded; default `None`, no limit |
| `failure_ttl` | how long failed jobs are kept; default 1 year |
| `depends_on` | a job (or list) that must finish successfully before this one is queued |
| `job_id`, `unique=True` | your own id; with `unique` a second enqueue of the same id raises `DuplicateJobError` (RQ 2.8+) |
| `retry` | `Retry(max=..., interval=...)`; intervals need a worker started with `--with-scheduler` |

The job function must live in a module the worker can import, not in `__main__`, and producer and worker must run the same code [50]. It must not depend on globals or a "current" web request [50]. RQ serialises jobs with pickle by default, which is not secure: use only Redis instances you trust, or `serializer='json'` on both sides [50].

## What a worker does

`rq worker high default low` listens on those queues in that order [50]. Each worker runs one job at a time; start more workers for concurrency [50]. For each job it marks itself busy, records the job in `StartedJobRegistry`, forks a child process (the work horse) that runs the job, then moves the job to `FinishedJobRegistry` or `FailedJobRegistry` [50]. Because of that fork, RQ workers only run where `fork()` exists: on Windows use WSL, or `SimpleWorker`, which runs jobs in the worker's own process and is meant for testing [50]. `--burst` drains the queues and exits [50]. On SIGTERM or Ctrl+C a worker lets the current job finish; a second signal kills the work horse [50].

| Status | Meaning [50] |
| --- | --- |
| `queued` | waiting in a queue |
| `started` | a worker is running it |
| `finished` | done; result kept for `result_ttl` |
| `failed` | raised, timed out, or expired before running |
| `deferred` | waiting for `depends_on` |
| `scheduled` | waiting for a future time, or for its next retry |
| `stopped`, `canceled` | stopped with its worker, or cancelled by hand |

`job.get_status()`, `job.return_value()` (only after a success) and `job.latest_result()` read the outcome; `Job.fetch(id, connection=...)` finds a job by id [50].

## Failure, retry, scheduling

A job that raises goes to `FailedJobRegistry`; `rq requeue --all` puts failed jobs back [50]. With `retry=Retry(max=2, interval=[2, 4])` the job is retried twice, after 2 and 4 seconds [50]. In the course's test run, a job that always failed moved like this:

```text
  0.0s job=started    vm=building  attempts=0
  2.4s job=scheduled  vm=building  attempts=1
  4.4s job=started    vm=building  attempts=1
  7.5s job=scheduled  vm=building  attempts=2
 11.5s job=started    vm=building  attempts=2
 14.5s job=failed     vm=error     attempts=3
```

`q.enqueue_in(timedelta(seconds=10), f)` and `q.enqueue_at(datetime, f)` schedule work; scheduled jobs wait in `ScheduledJobRegistry`, and only one scheduler per queue is active at a time [50].

## Idempotent jobs

Retries, a requeue by hand, or a worker killed with `kill -9` mid-job (which gets no chance to mark the job failed [50]) all mean the same job can run more than once. So write the job as "make the world look like X", not "do X": read the current state, do nothing if it is already done, and resume if an earlier run stopped halfway. The lab's job checks the VM status first and finishes quietly for `active`, `error`, `deleted` or a missing record.

## Redis for the parts around the queue

| Type | Definition [51] | In the VM API |
| --- | --- | --- |
| String | a sequence of bytes | idempotency key, a lock |
| Hash | field-value pairs, like a dict | `vm:<id>` record |
| List | strings in insertion order; push and pop at both ends | a simple queue |
| Set | unordered unique strings | ids of VMs on a host |
| Sorted set | unique strings ordered by a score | a time-ordered registry |
| Stream | an append-only log with consumer groups | an event feed |

**Expiry.** `EXPIRE key seconds` deletes the key later; `TTL key` returns the seconds left, `-1` for no expiry and `-2` for no key [51]. `SET` and `DEL` clear an expiry; `HSET` and `INCR` keep it [51].

**Persistence.** RDB writes point-in-time snapshots, so you may lose the last minutes; AOF logs every write and with the default fsync every second loses at most about a second [51]. The docs suggest both for safety close to a database [51].

**A simple lock.** `SET lock:vm:42 <random token> NX EX 10` succeeds only if the key does not exist, and expires on its own [51]. Release it with a small Lua script that deletes the key only if it still holds your token, so you never delete a lock that expired and was taken by someone else [51]. The Redis page itself prefers the Redlock algorithm for stronger guarantees [51].

:::low-confidence
Limits of the single-key lock that the notes do not spell out: if the holder pauses longer than the expiry, a second client can take the lock while the first still works, and a Redis failover can lose the key. Treat it as protection against accidental overlap, not as a correctness guarantee; check the Redis distributed locks page before relying on it.
:::

## Making POST retries safe: Idempotency-Key

An IETF draft (revision -08, October 2026, not yet an RFC) defines an `Idempotency-Key` request header: a unique client-generated value, such as a UUID, that lets the server recognise a retry of the same POST [58]. The draft says the server should answer 400 if a required key is missing, 422 if the key is reused with a different payload, and 409 if the first request is still being processed [58]. Stripe, as one vendor's practice, stores the first response for a key (even a 500), may prune keys after 24 hours, and limits keys to 255 characters [59].

## Gotchas

- **Defining the job in the script you run.** Functions in `__main__` cannot be enqueued; put them in a module. [50]
- **Retry interval without a scheduler.** `Retry(interval=...)` needs `rq worker --with-scheduler`. [50]
- **Running the worker on Windows.** The default worker forks; use WSL or Docker. [50]
- **Default 180 s timeout.** A long build is killed and marked failed; set `job_timeout`. [50]
- **Non-idempotent jobs.** Any retry or requeue then repeats side effects; check state first.
- **Lock without a token.** A plain `DEL` can release someone else's lock after yours expired. [51]

:::key-takeaways
- Return 202 fast, let a worker do the slow part, poll a status URL. [46] [52]
- One job at a time per worker, a forked work horse per job, so no native Windows. [50]
- Know the defaults: 180 s timeout, 500 s result TTL, failed jobs kept 1 year. [50]
- Retries with intervals need `--with-scheduler`; jobs must be idempotent. [50]
- `SET key token NX EX n` plus compare-and-delete is the simple lock. [51]
- Idempotency-Key is a draft; 400 missing, 422 different payload, 409 still running. [58]
:::

:::glossary
- **Task queue**: a list of work items that separate worker processes take and run.
- **Worker**: a long-running process that takes jobs from a queue and runs them.
- **Work horse**: the child process an RQ worker forks to run one job.
- **Registry**: a Redis set where RQ tracks jobs in one state, such as started or failed.
- **TTL (time to live)**: how long a key or job is kept before it is removed.
- **RDB**: Redis snapshots of all data written to a file at intervals.
- **AOF**: the Redis append-only file that logs every write.
- **Idempotency key**: a unique value a client sends so the server can recognise a retried request.
:::
