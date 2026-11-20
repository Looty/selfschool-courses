"""VM request API, FastAPI version. Same Redis records and job as app.py.

Differences from the Flask version: the body is a Pydantic model, so a bad
body gets FastAPI's 422 instead of our 400; errors use FastAPI's
{"detail": ...} shape; the handlers are plain `def` because redis-py is a
blocking client, so FastAPI runs them in its threadpool.

Run locally:  uvicorn app_fastapi:create_app --factory --reload
Production:   uvicorn app_fastapi:create_app --factory --host 0.0.0.0 --port 8000 --workers 3
"""
import os
import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from redis import Redis
from rq import Queue

import tasks

DELETED_TTL = 3600
IDEMPOTENCY_TTL = 86400


class VMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")   # unknown fields are a 422

    name: str = Field(min_length=1, max_length=63)
    cpus: int = Field(ge=1, le=64)
    memory_mb: int = Field(ge=256, le=1048576)
    fail: bool = False


class VM(BaseModel):
    id: str
    name: str
    cpus: int
    memory_mb: int
    status: str
    attempts: int = 0
    error: str | None = None


def create_app(vm_redis=None, vm_queue=None):
    """Application factory. Tests pass fakes; production reads REDIS_URL."""
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if vm_redis is None:
        vm_redis = Redis.from_url(url, decode_responses=True)
    if vm_queue is None:
        vm_queue = Queue(tasks.QUEUE_NAME, connection=Redis.from_url(url))

    app = FastAPI(title="VM request API")

    def find_vm(vm_id: str) -> dict:
        record = vm_redis.hgetall(tasks.vm_key(vm_id))
        if not record or record["status"] == "deleted":
            raise HTTPException(status_code=404, detail=f"vm {vm_id} not found")
        return record

    @app.post("/vms", status_code=202, response_model=VM, response_model_exclude_none=True)
    def create_vm(body: VMRequest, response: Response,
                  idempotency_key: Annotated[str | None, Header()] = None):
        vm_id = uuid.uuid4().hex[:12]
        if idempotency_key:
            if not vm_redis.set(f"idem:{idempotency_key}", vm_id, nx=True, ex=IDEMPOTENCY_TTL):
                earlier = vm_redis.hgetall(tasks.vm_key(vm_redis.get(f"idem:{idempotency_key}")))
                if not earlier:
                    raise HTTPException(status_code=409,
                                        detail="a request with this Idempotency-Key is still being processed")
                response.headers["Location"] = f"/vms/{earlier['id']}"
                return earlier
        record = {
            "id": vm_id, "status": "requested", "fail": "1" if body.fail else "0",
            "name": body.name, "cpus": str(body.cpus), "memory_mb": str(body.memory_mb),
        }
        vm_redis.hset(tasks.vm_key(vm_id), mapping=record)
        vm_queue.enqueue(tasks.provision, vm_id, job_id=f"provision-{vm_id}",
                         job_timeout=tasks.JOB_TIMEOUT, retry=tasks.RETRY)
        response.headers["Location"] = f"/vms/{vm_id}"
        return record

    @app.get("/vms/{vm_id}", response_model=VM, response_model_exclude_none=True)
    def get_vm(record: Annotated[dict, Depends(find_vm)]):
        return record

    @app.delete("/vms/{vm_id}", status_code=204)
    def delete_vm(vm_id: str):
        allowed = ("requested", "building", "active", "error")
        if tasks.transition(vm_redis, vm_id, allowed, "deleted") == "deleted":
            vm_redis.expire(tasks.vm_key(vm_id), DELETED_TTL)

    @app.get("/healthz")
    def healthz():
        vm_redis.ping()
        return {"status": "ok"}

    return app
