---
id: l12
title: "A Flask API with an RQ job queue"
quiz: quiz-12.yaml
resources: [../resources/ch05/vmapi/app.py, ../resources/ch05/vmapi/tasks.py, ../resources/ch05/vmapi/fakes.py, ../resources/ch05/vmapi/test_api.py, ../resources/ch05/vmapi/app_fastapi.py, ../resources/ch05/vmapi/test_api_fastapi.py, ../resources/ch05/vmapi/requirements.txt, ../resources/ch05/vmapi/Dockerfile, ../resources/ch05/vmapi/compose.yaml, ../resources/ch05/vmapi/smoke.sh]
sources: [45, 46, 48, 50, 51, 52, 55, 58]
---
After this lesson you can choose methods and status codes for a VM API, write it in Flask, queue the slow build with RQ, and run the stack.

## Methods and status codes

**Safe** asks for no change; **idempotent** means many sends have the effect of one, so only these may be retried automatically [52].

| Method | Safe | Idempotent |
| --- | --- | --- |
| GET, HEAD, OPTIONS | yes | yes |
| PUT, DELETE | no | yes |
| POST | no | no |

| Code | Use in the VM API |
| --- | --- |
| 200 / 204 | read a VM / deleted, no body [52] |
| 201 Created | the resource exists now [52] |
| 202 Accepted | accepted, not finished: `POST /vms` with a queue [52] |
| 400 / 409 / 422 | bad JSON / duplicate name / content invalid [52] |
| 401 / 403 | no credentials / known caller, refused [52] |
| 502 / 504 | gateway got a bad answer / no answer in time [52] |

## Flask in one screen

```python
bp = Blueprint("vms", __name__)

@bp.get("/vms/<int:vm_id>")         # only GET unless told otherwise
def get_vm(vm_id):
    vm = current_app.config["STORE"].get(vm_id)
    if vm is None:
        abort(404, description="not found")   # raises
    return vm                       # dict -> JSON, 200

@bp.delete("/vms/<int:vm_id>")
def delete_vm(vm_id):
    current_app.config["STORE"].pop(vm_id, None)
    return "", 204                  # (body, status[, headers])

def create_app():                   # factory: a fresh app per test
    app = Flask(__name__)
    app.config["STORE"] = {}
    app.register_blueprint(bp)
    app.register_error_handler(HTTPException,
        lambda e: (jsonify(error=e.description), e.code))
    return app
```

The error handler must return its own code, or it answers 200; register it on the app, not the blueprint [46]. `app.test_client()` tests without a server. Production runs `gunicorn -w 4 'app:create_app()'`, never `flask run --debug` [45] [46].

**FastAPI in brief.** Flask is a WSGI app: one synchronous call per request [46] [55]. FastAPI is an ASGI framework, async with events both ways, run by Uvicorn [48] [55]. It validates bodies itself and answers 422 [48].

## RQ: return 202, let a worker build

A build takes minutes, so `POST /vms` stores the record, enqueues only the VM id and answers 202 with `Location` [46] [52].

```python
q = Queue("vms", connection=Redis())
q.enqueue(provision, vm_id, job_id=f"provision-{vm_id}",
          job_timeout=60, retry=Retry(max=2, interval=[2, 4]))
```

What to know cold [50]:

- The job function lives in an importable module, not `__main__`.
- `rq worker vms` runs one job at a time in a forked work horse: no native Windows.
- Defaults: `job_timeout` 180 s, `result_ttl` 500 s, failed jobs kept 1 year.
- Retry intervals need `rq worker --with-scheduler`.

**Idempotent jobs.** Retries, requeues and `kill -9` can run a job twice, so read the VM status first: skip `active`, `error` or `deleted`, resume `building`.

**Redis lock:** `SET lock:vm:42 <token> NX EX 10`, deleted only if the token still matches [51]. The draft **Idempotency-Key** header makes POST retries safe [58].

## Lab: run the stack (30 minutes)

1. `cd resources/ch05/vmapi`, make a venv, `pip install -r requirements.txt`.
2. `python -m unittest test_api test_api_fastapi` (no Redis needed): expect `Ran 21 tests`, `OK`.
3. `docker compose up -d --build --wait` starts Redis, the Flask API (Gunicorn), a FastAPI copy and a worker with `--with-scheduler`.
4. `bash smoke.sh`, then `bash smoke.sh http://127.0.0.1:8809` (FastAPI). Watch `requested -> building -> active`, DELETE giving 204 twice, and a failing build ending in `error` after 3 attempts.
5. Start a build, then `docker compose kill -s SIGKILL worker` and later `docker compose start worker`. The VM stays `building` until a worker cleans up and reruns the idempotent job.
6. `docker compose down -v --rmi local`; read `tasks.py` as the solution.

:::low-confidence
Step 5 comes from one run. RQ's docs say an abandoned job ends up in `FailedJobRegistry` [50]; here, with retries left, it ran again and finished. Check your RQ version before relying on either.
:::

:::key-takeaways
- Safe: GET, HEAD, OPTIONS. Idempotent: those plus PUT and DELETE. POST is neither. [52]
- 201 means created now; 202 means accepted for later; 204 means done, no body. [52]
- Flask: dict means JSON, tuple sets status, error handlers must return their own code. [45] [46]
- RQ: 180 s default timeout; retry intervals need `--with-scheduler`; jobs must be idempotent. [50]
:::
