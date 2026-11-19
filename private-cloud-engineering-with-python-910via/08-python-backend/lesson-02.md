---
id: l22
title: "FastAPI, Pydantic, and WSGI vs ASGI"
quiz: quiz-02.yaml
resources: [../resources/ch08/fastapi_drill/app_starter.py, ../resources/ch08/fastapi_drill/app_solution.py, ../resources/ch08/fastapi_drill/app_test.py]
sources: [45, 46, 48, 49, 54, 55, 56, 57]
---
After this lesson you can write the VM API in FastAPI with typed parameters, a Pydantic body, a response model and a dependency, avoid the blocking call that freezes an async server, and explain WSGI, ASGI, Gunicorn and Uvicorn in two sentences each.

## Parameters come from the type hints

FastAPI reads the function signature to decide where each value comes from [48]:

- a name that appears in the path string is a **path parameter**;
- a plain type such as `int`, `str` or `bool` is a **query parameter**;
- a Pydantic model is the **request body**, read as JSON.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class VMCreate(BaseModel):
    name: str
    cpus: int
    memory_mb: int = 2048          # a default makes the field optional

app = FastAPI()

@app.get("/vms/{vm_id}")
def get_vm(vm_id: int, verbose: bool = False):
    ...

@app.post("/vms", status_code=202)
def create_vm(body: VMCreate):
    return {"id": 1, "status": "requested", **body.model_dump()}
```

`vm_id` arrives as a Python `int`; `/vms/foo` never reaches your code [48]. A query parameter with a default is optional, without one it is required [48]. `body.model_dump()` turns the model into a dict [48]. `status_code=` on the decorator sets the success code [48].

## 422: the validation error you did not write

When the path, query or body does not fit the types, FastAPI raises `RequestValidationError` internally and its default handler answers **422** with `{"detail": [...]}` [48]. Each entry says where and what [48]:

```json
{"detail": [{"type": "int_parsing", "loc": ["path", "item_id"],
  "msg": "Input should be a valid integer, unable to parse string as an integer",
  "input": "foo"}]}
```

Compare Flask in lesson 1, where you write the 400 yourself. In the drill, `Field(ge=1, le=64)` adds a range check; in the course's test run `cpus: 0` gave 422 with `"type": "greater_than_equal"` and `"loc": ["body", "cpus"]`.

## Errors, response models and dependencies

- **`HTTPException`** is raised, not returned: `raise HTTPException(status_code=404, detail="vm 7 not found")` ends the request with body `{"detail": "vm 7 not found"}` [48].
- **`response_model=VM`** on the decorator (or a return type annotation) validates the output and filters it to the model's fields [48]. Use it to keep internal fields, such as a password or our `fail` flag, out of responses [48]. If your code returns data that does not fit, FastAPI answers with a server error rather than wrong data [48].
- **`Depends`**: a dependency is a function FastAPI calls before your handler, passing its result in [48]. Pass the function itself, without calling it [48]. "Find this VM or 404" is a natural dependency:

```python
def find_vm(vm_id: int) -> dict:
    vm = STORE.get(vm_id)
    if vm is None:
        raise HTTPException(status_code=404, detail=f"vm {vm_id} not found")
    return vm

@app.get("/vms/{vm_id}", response_model=VM)
def get_vm(vm: Annotated[dict, Depends(find_vm)]):
    return vm
```

The `Annotated` form is the one the docs prefer [48].

## `def` or `async def`: the blocking trap

A handler declared with plain `def` "is run in an external threadpool that is then awaited" [48]. A handler declared with `async def` runs directly on the event loop, so a blocking call inside it stops every other request until it returns. The docs' rules: if a library tells you to `await` it, use `async def`; if a library does not support `await` (most database libraries, they note), use `def`; if the handler waits for nothing at all, `async def` is fine; if you just don't know, use `def` [48].

The course's test run sent five concurrent requests to three handlers that each wait one second:

```text
5 concurrent GET /async-blocking   5.0 s     async def + time.sleep(1)
5 concurrent GET /sync-blocking    1.1 s     def       + time.sleep(1)
5 concurrent GET /async-awaiting   1.0 s     async def + await asyncio.sleep(1)
```

`time.sleep` stands in for any blocking client: redis-py, `requests`, `subprocess.run`, a libvirt call. That is why the lab's FastAPI handlers are plain `def`.

## BackgroundTasks and its limits

`BackgroundTasks.add_task(func, *args)` runs a function after the response is sent [48]. The docs suggest it for small tasks, and point to bigger tools (they name Celery, with a queue such as RabbitMQ or Redis) for heavy work that should run in other processes or on other servers [48]. For VM provisioning that matters: the task lives inside the API process, so a deploy or a crash of that process takes any unfinished task with it. Lesson 3 uses RQ instead.

## Testing

`TestClient(app)` comes from Starlette and is built on HTTPX, so install `httpx` [49]. Tests are plain `def` functions and calls are not awaited [49]. Pass `json=` for a body and `headers=` for headers; read `response.json()` [49].

## WSGI, ASGI and the servers

| | WSGI | ASGI |
| --- | --- | --- |
| Interface | `application(environ, start_response)` returns an iterable of bytes [54] | `async def application(scope, receive, send)` [55] |
| Shape | one synchronous call per request [55] | events in and out, so WebSockets and long-poll work [55] |
| Frameworks | Flask is a WSGI application [46] | FastAPI is an ASGI framework [48] |
| Typical server | Gunicorn, pre-fork arbiter plus worker processes [56] | Uvicorn [57] |

Gunicorn's default **sync worker** handles one request at a time per worker process [56]; Gunicorn suggests starting with `(2 x CPU cores) + 1` workers [56]. Uvicorn listens on `127.0.0.1:8000` by default, takes `--workers N` (not together with `--reload`), and calls an app factory with `uvicorn --factory main:create_app` [57]; it starts worker processes with spawn rather than pre-fork, so its process manager works on Windows [57]. Uvicorn's docs also recommend running it under Gunicorn with a Uvicorn worker class, while warning that the `uvicorn.workers` module is deprecated in favour of a separate package [57]. ASGI servers can run WSGI apps through an adapter with a threadpool [55].

| | Flask 3.1.3 [45] | FastAPI 0.165.0 [48] |
| --- | --- | --- |
| Bad input | you validate, you return 400 | automatic 422 |
| Docs | none built in | `/docs`, `/redoc`, `/openapi.json` [48] |
| Errors | `abort(404)`, handler returns its status | `raise HTTPException(404)` [48] |
| Tests | `app.test_client()` | `TestClient(app)` [49] |

FastAPI is still on 0.x and releases often: six releases between 2026-11-13 and 2026-11-18, the latest 0.165.0 [48]. Pin the version you tested.

## Drill: the same inventory in FastAPI (15 minutes)

```bash
python -m pip install fastapi==0.165.0 httpx==0.28.1
python app_test.py                  # your app_starter.py
python app_test.py app_solution     # the reference
```

In the course's test run the solution printed `Ran 12 tests` and `OK` on Python 3.13 and 3.11, and the starter failed all 12 with `NotImplementedError`. Starlette 1.10.0 also printed a deprecation warning suggesting `httpx2` instead of `httpx` for the test client; the tests still passed. Contract: as the Flask drill, except invalid input is FastAPI's 422 and errors use `detail`.

**Hints.** Define the routes inside `create_app()` so they close over that app's store. Use `Field(min_length=1)` and `Field(ge=..., le=...)`. A 204 handler returns nothing.

**Walkthrough.** The reference declares `status_code=201, response_model=VM` on POST, raises 409 for a duplicate name, and uses `find_vm` through `Depends` for GET. `GET /vms/abc` gives 422 with `"loc": ["path", "vm_id"]` before any of your code runs. GET and DELETE by id are O(1); the duplicate-name scan makes POST O(n), which a second dict from name to id would make O(1). The usual slip is writing `return HTTPException(...)`: in the course's test run that answered `200 {"status_code":404,"detail":"vm not found","headers":null}`, an error serialised as a success.

## Gotchas

- **Blocking inside `async def`.** One `time.sleep` or redis-py call stalls the event loop for every client; use `def`. [48]
- **Returning instead of raising `HTTPException`.** Only `raise` ends the request with the error status. [48]
- **Calling the dependency.** `Depends(find_vm())` passes a result, not the function. [48]
- **Trusting BackgroundTasks for durable work.** It runs inside the API process, so a restart loses unfinished tasks; the docs point heavy work to a real queue. [48]
- **Expecting 400 for bad bodies.** FastAPI's default is 422 with a list in `detail`; tests and clients must expect that. [48]
- **Unpinned FastAPI.** A 0.x project that releases several times a week can change under you. [48]

:::key-takeaways
- Path string name means path parameter, plain type means query, Pydantic model means body. [48]
- Invalid input gives 422 with `{"detail": [...]}` automatically. [48]
- `response_model` validates and filters output; `Depends` injects shared lookups. [48]
- `def` handlers run in a threadpool; blocking code inside `async def` blocks everyone. [48]
- WSGI is one synchronous call per request; ASGI is async with events, needed for WebSockets. [54] [55]
- Gunicorn pre-forks sync workers; Uvicorn serves ASGI and spawns workers. [56] [57]
:::

:::glossary
- **Pydantic model**: a class whose typed fields are checked and converted when data is loaded into it.
- **Path parameter**: a value taken from a part of the URL path, such as the 7 in `/vms/7`.
- **Query parameter**: a value from the part of the URL after `?`.
- **Dependency**: a function FastAPI runs before a handler and whose result it passes in.
- **Event loop**: the single scheduler that runs async code and switches tasks only at `await`.
- **Threadpool**: a set of reusable threads that run blocking functions so the event loop stays free.
- **WSGI**: the standard synchronous interface between Python web servers and web apps.
- **ASGI**: the asynchronous successor to WSGI, with event messages in both directions.
- **Pre-fork**: starting worker processes in advance by copying a parent process.
:::
