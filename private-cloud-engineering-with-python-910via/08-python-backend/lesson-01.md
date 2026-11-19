---
id: l21
title: "HTTP semantics and Flask"
quiz: quiz-01.yaml
resources: [../resources/ch08/flask_drill/app_starter.py, ../resources/ch08/flask_drill/app_solution.py, ../resources/ch08/flask_drill/app_test.py]
sources: [45, 46, 47, 52, 53]
---
After this lesson you can choose the right method and status code for each route of a VM API, write that API in Flask with a blueprint, an application factory and JSON errors, and test it without starting a server.

## The running example

This chapter builds one service in four steps. `POST /vms` validates a request, records it, puts a provisioning job on a queue and answers at once with an id and a status. A worker process does the slow part. `GET /vms/{id}` reports progress, and `DELETE /vms/{id}` can be repeated safely. This lesson covers the HTTP rules and the Flask code; the queue comes in lesson 3 of this chapter.

## Safe and idempotent methods

A method is **safe** when the client asks for no change on the server: it is essentially read-only [52]. A method is **idempotent** when sending the same request many times has the same intended effect as sending it once [52]. The server may still log each call; the property is about what the client asked for [52].

| Method | Safe | Idempotent | In the VM API |
| --- | --- | --- | --- |
| GET, HEAD, OPTIONS | yes | yes | read a VM |
| PUT | no | yes | replace a whole record (not used here) |
| DELETE | no | yes | delete a VM |
| POST | no | no | create a VM request |

Source for the table: RFC 9110's method registry [52].

Why it matters: an idempotent request can be repeated automatically after a network failure, while a client should not retry a non-idempotent one unless it knows the retry is harmless [52]. A proxy must never retry one on its own [52]. That is why a lost response to `POST /vms` is dangerous (two VMs?) and a lost response to `DELETE /vms/7` is not. Lesson 3 adds the `Idempotency-Key` header to make POST retries safe.

## Status codes you will actually use

| Code | Meaning (RFC 9110 unless marked) | In the VM API |
| --- | --- | --- |
| 200 OK | succeeded; body is the result [52] | `GET /vms/7` |
| 201 Created | a new resource exists now, named by `Location` [52] | a synchronous create (the drill) |
| 202 Accepted | accepted, processing not finished [52] | `POST /vms` with a queue |
| 204 No Content | succeeded, no body [52] | `DELETE /vms/7` |
| 400 Bad Request | client error such as malformed syntax [52] | body is not JSON |
| 401 Unauthorized | no valid credentials; must send `WWW-Authenticate` [52] | missing token |
| 403 Forbidden | understood, refused; credentials are insufficient [52] | user may not delete others' VMs |
| 404 Not Found | no such resource, or the server will not say [52] | unknown id |
| 409 Conflict | clashes with the resource's current state [52] | duplicate VM name |
| 422 Unprocessable Content | syntax fine, content cannot be processed [52] | `cpus: 0` (FastAPI's default) |
| 429 Too Many Requests | rate limited; may send `Retry-After` (RFC 6585) [53] | quota of requests exceeded |
| 500 Internal Server Error | unexpected condition [52] | unhandled exception |
| 502 Bad Gateway | proxy got an invalid response from upstream [52] | nginx in front of a crashed app |
| 503 Service Unavailable | overloaded or in maintenance [52] | Redis is down |
| 504 Gateway Timeout | proxy got no timely response [52] | upstream hung |

Two pairs people mix up: 401 means "who are you?", 403 means "I know, and no" [52]. 502 and 504 both come from a gateway; 502 is a bad answer, 504 is no answer in time [52]. 429 is not in RFC 9110 at all; it comes from RFC 6585 [53].

## Flask in one screen

```python
from flask import Blueprint, Flask, abort, current_app, jsonify
from werkzeug.exceptions import HTTPException

bp = Blueprint("vms", __name__)

@bp.get("/vms/<int:vm_id>")
def get_vm(vm_id):
    vm = current_app.config["STORE"]["vms"].get(vm_id)
    if vm is None:
        abort(404, description=f"vm {vm_id} not found")
    return vm                                   # dict -> JSON, 200

@bp.delete("/vms/<int:vm_id>")
def delete_vm(vm_id):
    current_app.config["STORE"]["vms"].pop(vm_id, None)
    return "", 204                              # (body, status)

def handle_http_error(error):
    return jsonify(error=error.description), error.code

def create_app():
    app = Flask(__name__)
    app.config["STORE"] = {"vms": {}, "next_id": 1}
    app.register_blueprint(bp)
    app.register_error_handler(HTTPException, handle_http_error)
    return app
```

The rules this relies on:

- A route answers only GET unless you list methods; `@bp.get`, `@bp.post` and friends are shortcuts [45]. `<int:vm_id>` converts the URL part to an integer [45].
- Returning a dict or list sends JSON; a tuple `(body, status)` or `(body, status, headers)` sets the code and headers [45].
- `abort(404)` raises an HTTP error that stops the view [45]. An error handler must return the status itself: Flask does not copy the handler's code into the response [46]. Registering for `HTTPException` turns every HTTP error into JSON [46].
- A **blueprint** records routes and registers them on an app later [46]. It cannot handle 404 for a URL nothing matched, because it owns no URL space, so register the JSON handler on the app [46].
- An **application factory** builds the app inside a function, so tests can make fresh instances with their own settings [46]. Inside a request, reach the app through `current_app` [46]. Flask finds a factory called `create_app` by itself [46].

## Testing without a server

`app.test_client()` sends requests to the app without running a live server [47]. Pass `json=` for a JSON body and read `response.json` back [47]:

```python
client = create_app().test_client()
r = client.post("/vms", json={"name": "web-1", "cpus": 2, "memory_mb": 2048})
assert r.status_code == 201 and r.headers["Location"] == "/vms/1"
```

## Why not the development server

`flask run` starts a server meant for local use; the docs say not to use it in production, because it is not designed to be secure, stable or efficient [46]. With `--debug` it runs a browser debugger that can execute arbitrary code [45]. Production uses a WSGI server such as Gunicorn, often behind nginx as a reverse proxy [46]: `gunicorn -w 4 'app:create_app()'` [46]. Gunicorn does not run on Windows (it does under WSL) [46]. Lesson 2 explains WSGI.

## Drill: the VM inventory in Flask (15 minutes)

```bash
python -m pip install flask==3.1.3
python app_test.py                  # tests your app_starter.py
python app_test.py app_solution     # tests the reference
```

The starter's docstring has the full contract: `POST /vms` returns 201 and a `Location` header, 400 for a bad body, 409 for a duplicate name; `GET /vms` lists by id; `GET /vms/<id>` returns 404 as JSON; `DELETE /vms/<id>` returns 204 every time. In the course's test run the solution printed `Ran 12 tests` and `OK` on Python 3.13 and 3.11, and the untouched starter failed all 12 with `NotImplementedError`.

**Hints.** Read the body with `request.get_json(silent=True)` and pass it to `validate_vm`; in the course's test run a plain-text body then came through as `None` and got the 400 the tests expect. Keep the store in `app.config` so two apps never share one. Pop with a default in DELETE.

**Walkthrough.** The reference keeps all state in `app.config["STORE"]`, reached through `current_app`. `flask --app "app_solution:create_app()" routes` printed this in the course's test run:

```text
Endpoint       Methods  Rule
-------------  -------  -----------------------
static         GET      /static/<path:filename>
vms.create_vm  POST     /vms
vms.delete_vm  DELETE   /vms/<int:vm_id>
vms.get_vm     GET      /vms/<int:vm_id>
vms.list_vms   GET      /vms
```

Endpoints carry the blueprint name as a prefix [46]. `PUT /vms` gave `405 {'error': 'The method is not allowed for the requested URL.'}` through the same JSON handler. GET and DELETE by id are O(1); the duplicate-name scan makes POST O(n).

## Gotchas

- **Error handler without a status.** `return jsonify(error=...)` from a handler answers 200. Return `(body, error.code)`. [46]
- **JSON handler on the blueprint only.** Unknown URLs then get Flask's HTML 404. Register it on the app. [46]
- **Module-level state.** A global dict is shared by every app and every test; the factory exists to avoid that. [46]
- **201 for work that has not happened.** If a worker builds the VM later, answer 202 and point to a status URL. [52]
- **Retrying POST blindly.** POST is not idempotent; a client must not resend it automatically without a key. [52]
- **Debug server in production.** `flask run --debug` exposes a code-executing debugger. [45]

:::key-takeaways
- Safe: GET, HEAD, OPTIONS. Idempotent: those plus PUT and DELETE. POST is neither. [52]
- 201 means created now; 202 means accepted for later; 204 means done, no body. [52]
- 401 is missing credentials, 403 is refusal; 502 is a bad upstream answer, 504 no answer in time; 429 is from RFC 6585. [52] [53]
- Flask: dict means JSON, tuple sets status and headers, handlers must return their own code. [45] [46]
- Factory plus blueprint plus test client gives isolated, server-free tests. [46] [47]
:::

:::glossary
- **Safe**: a method that asks the server to change nothing.
- **Idempotent**: repeating the same request has the same intended effect as sending it once.
- **Blueprint**: a bundle of Flask routes that is attached to an application later.
- **Application factory**: a function that builds and returns a new configured app.
- **Test client**: an object that calls the app's routes directly, with no network or server.
- **WSGI server**: a program that receives HTTP and calls a Python web app in the standard WSGI way.
- **Reverse proxy**: an HTTP server such as nginx that sits in front of the app server and forwards requests to it.
- **Endpoint**: the internal name Flask gives a route, such as `vms.get_vm`.
:::
