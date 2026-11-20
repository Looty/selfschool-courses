"""VM request API (Flask): records a request, queues the build, answers 202.

    POST   /vms        validate, store vm:<id>, enqueue tasks.provision -> 202
    GET    /vms/<id>   current status -> 200, or 404
    DELETE /vms/<id>   mark deleted (idempotent) -> 204
    GET    /healthz    Redis reachable -> 200

Run locally:  flask --app app run        (finds create_app by itself)
Production:   gunicorn -w 3 -b 0.0.0.0:8000 'app:create_app()'
"""
import os
import uuid

from flask import Blueprint, Flask, abort, current_app, jsonify, request
from redis import Redis
from rq import Queue
from werkzeug.exceptions import HTTPException

import tasks

bp = Blueprint("vms", __name__)

DELETED_TTL = 3600         # seconds a deleted record is kept before Redis drops it
IDEMPOTENCY_TTL = 86400    # seconds an Idempotency-Key is remembered
FIELDS = ("name", "cpus", "memory_mb")


def validate(data):
    """Return an error message for a bad request body, or None when it is valid."""
    if not isinstance(data, dict):
        return "body must be a JSON object"
    unknown = set(data) - set(FIELDS) - {"fail"}
    if unknown:
        return f"unknown fields: {', '.join(sorted(unknown))}"
    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 63:
        return "name must be a string of 1 to 63 characters"
    for field, low, high in (("cpus", 1, 64), ("memory_mb", 256, 1048576)):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, int):
            return f"{field} must be an integer"
        if not low <= value <= high:
            return f"{field} must be between {low} and {high}"
    if not isinstance(data.get("fail", False), bool):
        return "fail must be true or false"
    return None


def public(record):
    """The fields a client sees, with numbers turned back into numbers."""
    vm = {
        "id": record["id"],
        "name": record["name"],
        "cpus": int(record["cpus"]),
        "memory_mb": int(record["memory_mb"]),
        "status": record["status"],
        "attempts": int(record.get("attempts", 0)),
    }
    if "error" in record:
        vm["error"] = record["error"]
    return vm


def accepted(record):
    return public(record), 202, {"Location": f"/vms/{record['id']}"}


@bp.post("/vms")
def create_vm():
    data = request.get_json(silent=True)
    error = validate(data)
    if error:
        abort(400, description=error)
    r = current_app.extensions["vm_redis"]
    vm_id = uuid.uuid4().hex[:12]

    key = request.headers.get("Idempotency-Key")
    if key:
        if not r.set(f"idem:{key}", vm_id, nx=True, ex=IDEMPOTENCY_TTL):
            earlier = r.hgetall(tasks.vm_key(r.get(f"idem:{key}")))
            if not earlier:
                abort(409, description="a request with this Idempotency-Key is still being processed")
            return accepted(earlier)

    record = {"id": vm_id, "status": "requested", "fail": "1" if data.get("fail") else "0"}
    record.update({field: str(data[field]) for field in FIELDS})
    r.hset(tasks.vm_key(vm_id), mapping=record)
    current_app.extensions["vm_queue"].enqueue(
        tasks.provision, vm_id,
        job_id=f"provision-{vm_id}",
        job_timeout=tasks.JOB_TIMEOUT,
        retry=tasks.RETRY,
    )
    return accepted(record)


@bp.get("/vms/<vm_id>")
def get_vm(vm_id):
    record = current_app.extensions["vm_redis"].hgetall(tasks.vm_key(vm_id))
    if not record or record["status"] == "deleted":
        abort(404, description=f"vm {vm_id} not found")
    return public(record)


@bp.delete("/vms/<vm_id>")
def delete_vm(vm_id):
    r = current_app.extensions["vm_redis"]
    allowed = ("requested", "building", "active", "error")
    if tasks.transition(r, vm_id, allowed, "deleted") == "deleted":
        r.expire(tasks.vm_key(vm_id), DELETED_TTL)
    return "", 204


@bp.get("/healthz")
def healthz():
    current_app.extensions["vm_redis"].ping()
    return {"status": "ok"}


def json_error(error):
    """Every HTTP error, including 404 and 405 from routing, becomes JSON."""
    return jsonify(error=error.name, detail=error.description), error.code


def unexpected_error(error):
    current_app.logger.exception("unhandled error")
    return jsonify(error="Internal Server Error", detail="unexpected error"), 500


def create_app(vm_redis=None, vm_queue=None):
    """Application factory. Tests pass fakes; production reads REDIS_URL."""
    app = Flask(__name__)
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if vm_redis is None:
        vm_redis = Redis.from_url(url, decode_responses=True)
    if vm_queue is None:
        # RQ stores its own data as bytes, so it gets a connection without decoding.
        vm_queue = Queue(tasks.QUEUE_NAME, connection=Redis.from_url(url))
    app.extensions["vm_redis"] = vm_redis
    app.extensions["vm_queue"] = vm_queue
    app.register_blueprint(bp)
    app.register_error_handler(HTTPException, json_error)
    app.register_error_handler(Exception, unexpected_error)
    return app
