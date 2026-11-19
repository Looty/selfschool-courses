"""Flatten nested JSON to dotted keys (drill, 5 to 8 minutes).

Configuration from an API often arrives as nested JSON. Flatten it into one
level so that it can be compared, diffed or written as key=value lines.

Input
    text: a JSON document as a string. Its top level must be an object.
    sep:  the separator between key parts (default ".").

Output
    A dict whose keys are paths and whose values are the leaves.
    - A nested object adds its key: {"a": {"b": 1}} -> {"a.b": 1}
    - A list adds the index: {"a": [10, 20]} -> {"a.0": 10, "a.1": 20}
    - Leaves are the decoded JSON scalars: str, int, float, True, False, None.
    - An empty object or empty list is itself a leaf: {"a": {}} -> {"a": {}}
    - Keys appear in document order (depth first).

Errors
    Raise ValueError if the text is not valid JSON, or if the top level is
    not an object. (json.JSONDecodeError is already a ValueError.)

Example 1
    json_flatten('{"vm": {"name": "web-1", "disks": [{"size": 20}, {"size": 100}]}}')
    -> {"vm.name": "web-1", "vm.disks.0.size": 20, "vm.disks.1.size": 100}

Example 2
    json_flatten('{"a": {"b": null}, "c": true}', sep="/")
    -> {"a/b": None, "c": True}

Example 3
    json_flatten('[1, 2]')   -> raises ValueError
"""


def json_flatten(text: str, sep: str = ".") -> dict:
    """Return the JSON object in text flattened to one level of path keys."""
    raise NotImplementedError
