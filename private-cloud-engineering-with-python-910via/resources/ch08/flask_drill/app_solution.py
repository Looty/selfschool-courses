"""Flask drill, reference solution: an in-memory VM inventory API.

The problem statement is in app_starter.py.
Check it with:  python app_test.py app_solution
"""
from flask import Blueprint, Flask, abort, current_app, jsonify, request
from werkzeug.exceptions import HTTPException

bp = Blueprint("vms", __name__)


def new_store():
    """Return an empty store: the VMs by id, and the next id to hand out."""
    return {"vms": {}, "next_id": 1}


def validate_vm(data):
    """Return an error message for a bad request body, or None when it is valid."""
    if not isinstance(data, dict):
        return "body must be a JSON object"
    name = data.get("name")
    if not isinstance(name, str) or not name:
        return "name must be a non-empty string"
    for field, low, high in (("cpus", 1, 64), ("memory_mb", 256, 1048576)):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, int):
            return f"{field} must be an integer"
        if not low <= value <= high:
            return f"{field} must be between {low} and {high}"
    return None


def store():
    """The store of the application that is handling the current request."""
    return current_app.config["STORE"]


@bp.post("/vms")
def create_vm():
    data = request.get_json(silent=True)
    error = validate_vm(data)
    if error:
        abort(400, description=error)
    s = store()
    if any(vm["name"] == data["name"] for vm in s["vms"].values()):
        abort(409, description=f"a vm named {data['name']} already exists")
    vm = {
        "id": s["next_id"],
        "name": data["name"],
        "cpus": data["cpus"],
        "memory_mb": data["memory_mb"],
        "status": "requested",
    }
    s["vms"][vm["id"]] = vm
    s["next_id"] += 1
    return vm, 201, {"Location": f"/vms/{vm['id']}"}


@bp.get("/vms")
def list_vms():
    vms = store()["vms"]
    return [vms[vm_id] for vm_id in sorted(vms)]


@bp.get("/vms/<int:vm_id>")
def get_vm(vm_id):
    vm = store()["vms"].get(vm_id)
    if vm is None:
        abort(404, description=f"vm {vm_id} not found")
    return vm


@bp.delete("/vms/<int:vm_id>")
def delete_vm(vm_id):
    store()["vms"].pop(vm_id, None)
    return "", 204


def handle_http_error(error):
    """Return every HTTP error as JSON, keeping its status code."""
    return jsonify(error=error.description), error.code


def create_app():
    """Build a Flask app with its own store, the blueprint and JSON errors."""
    app = Flask(__name__)
    app.config["STORE"] = new_store()
    app.register_blueprint(bp)
    app.register_error_handler(HTTPException, handle_http_error)
    return app


# Complexity: GET and DELETE by id are O(1) dictionary operations. POST is
# O(n) in the number of VMs because of the duplicate-name scan, and GET /vms
# is O(n log n) for the sort; the store takes O(n) space.
# Alternative: keep a second dictionary from name to id, so the duplicate
# check is O(1) at the cost of updating two structures on create and delete.
