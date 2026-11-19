"""Flask drill: an in-memory VM inventory API. Time box: 15 minutes.

Write a blueprint with four routes and an application factory.

Routes (all bodies are JSON):

    POST /vms
        Request body: {"name": "web-1", "cpus": 2, "memory_mb": 2048}
        201  the stored VM: {"id": 1, "name": "web-1", "cpus": 2,
                             "memory_mb": 2048, "status": "requested"}
             plus the header  Location: /vms/1
        400  {"error": "<message>"} when validate_vm() returns a message
        409  {"error": "<message>"} when a VM with that name already exists

    GET /vms
        200  a JSON list of all VMs, ordered by id ([] when empty)

    GET /vms/<id>
        200  the VM
        404  {"error": "<message>"} when there is no VM with that id

    DELETE /vms/<id>
        204  empty body, whether or not the VM existed (idempotent)

Factory:

    create_app() returns a new Flask app with
      - its own store:  app.config["STORE"] = new_store()
      - the blueprint registered
      - an error handler that turns every HTTP error (404 for an unknown
        URL, 405 for a wrong method, the 400/404/409 you abort with) into
        JSON of the form {"error": "<description>"} with the right status

Constraints:
    ids are integers starting at 1 and are never reused within one app;
    two apps made by create_app() must not share VMs.

Examples:
    POST /vms {"name": "web-1", "cpus": 2, "memory_mb": 2048}  -> 201, id 1
    POST /vms {"name": "web-1", "cpus": 4, "memory_mb": 4096}  -> 409
    POST /vms {"name": "db-1", "cpus": 0, "memory_mb": 4096}   -> 400
    DELETE /vms/1 -> 204, and again DELETE /vms/1 -> 204
    GET /vms/1 -> 404

Check your work:  python app_test.py
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


# Write the four routes on bp here.


def create_app():
    """Build a Flask app with its own store, the blueprint and JSON errors."""
    raise NotImplementedError
