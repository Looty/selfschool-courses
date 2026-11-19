"""FastAPI drill, reference solution: an in-memory VM inventory API.

The problem statement is in app_starter.py.
Check it with:  python app_test.py app_solution
"""
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def new_store():
    """Return an empty store: the VMs by id, and the next id to hand out."""
    return {"vms": {}, "next_id": 1}


class VMCreate(BaseModel):
    name: str = Field(min_length=1)
    cpus: int = Field(ge=1, le=64)
    memory_mb: int = Field(ge=256, le=1048576)


class VM(BaseModel):
    id: int
    name: str
    cpus: int
    memory_mb: int
    status: str


def create_app():
    """Build a FastAPI app with its own store and the four routes."""
    app = FastAPI(title="VM inventory")
    store = new_store()

    def find_vm(vm_id: int):
        vm = store["vms"].get(vm_id)
        if vm is None:
            raise HTTPException(status_code=404, detail=f"vm {vm_id} not found")
        return vm

    @app.post("/vms", status_code=201, response_model=VM)
    def create_vm(body: VMCreate):
        if any(vm["name"] == body.name for vm in store["vms"].values()):
            raise HTTPException(status_code=409, detail=f"a vm named {body.name} already exists")
        vm = {"id": store["next_id"], "status": "requested", **body.model_dump()}
        store["vms"][vm["id"]] = vm
        store["next_id"] += 1
        return vm

    @app.get("/vms", response_model=list[VM])
    def list_vms():
        return [store["vms"][vm_id] for vm_id in sorted(store["vms"])]

    @app.get("/vms/{vm_id}", response_model=VM)
    def get_vm(vm: Annotated[dict, Depends(find_vm)]):
        return vm

    @app.delete("/vms/{vm_id}", status_code=204)
    def delete_vm(vm_id: int):
        store["vms"].pop(vm_id, None)

    return app


# Complexity: GET and DELETE by id are O(1) dictionary operations. POST is
# O(n) in the number of VMs because of the duplicate-name scan, and GET /vms
# is O(n log n) for the sort; the store takes O(n) space.
# Alternative: a module-level `app = FastAPI()` with a module-level store,
# as most tutorials do; it is shorter, but every test then shares one store
# and has to reset it.
