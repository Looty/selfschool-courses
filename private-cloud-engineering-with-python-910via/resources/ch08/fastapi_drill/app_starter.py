"""FastAPI drill: the same in-memory VM inventory API. Time box: 15 minutes.

Write two Pydantic models and an application factory with four routes.

Models:

    VMCreate   the request body
        name: str        at least 1 character
        cpus: int        1 to 64
        memory_mb: int   256 to 1048576

    VM         what the API returns
        id: int, name: str, cpus: int, memory_mb: int, status: str

Routes (all bodies are JSON):

    POST /vms            body: VMCreate
        201  the stored VM, with "status": "requested"
        422  FastAPI's validation error when the body does not fit VMCreate
        409  {"detail": "<message>"} when a VM with that name already exists

    GET /vms
        200  a JSON list of all VMs, ordered by id ([] when empty)

    GET /vms/{vm_id}
        200  the VM
        404  {"detail": "<message>"} when there is no VM with that id
        422  when vm_id is not an integer

    DELETE /vms/{vm_id}
        204  empty body, whether or not the VM existed (idempotent)

Factory:

    create_app() returns a new FastAPI app whose routes use their own
    new_store(), so two apps never share VMs. Define the routes inside
    create_app() so they can see the store.

Constraints:
    ids are integers starting at 1 and are never reused within one app;
    declare the response shape with response_model and the success status
    with status_code; use a dependency (Depends) for "find this VM or 404".

Examples:
    POST /vms {"name": "web-1", "cpus": 2, "memory_mb": 2048}  -> 201, id 1
    POST /vms {"name": "web-1", "cpus": 4, "memory_mb": 4096}  -> 409
    POST /vms {"name": "db-1", "cpus": 0, "memory_mb": 4096}   -> 422
    DELETE /vms/1 -> 204, and again DELETE /vms/1 -> 204
    GET /vms/1 -> 404

Check your work:  python app_test.py
"""
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def new_store():
    """Return an empty store: the VMs by id, and the next id to hand out."""
    return {"vms": {}, "next_id": 1}


# Define VMCreate and VM here.


def create_app():
    """Build a FastAPI app with its own store and the four routes."""
    raise NotImplementedError
