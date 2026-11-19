"""Reference solution for json_flatten (see json_flatten_starter.py)."""
import json


def json_flatten(text: str, sep: str = ".") -> dict:
    """Return the JSON object in text flattened to one level of path keys."""
    data = json.loads(text)  # raises json.JSONDecodeError, a ValueError
    if not isinstance(data, dict):
        raise ValueError(f"top level must be an object, got {type(data).__name__}")

    flat = {}

    def walk(value, prefix):
        if isinstance(value, dict) and value:
            for key, child in value.items():
                walk(child, f"{prefix}{sep}{key}")
        elif isinstance(value, list) and value:
            for index, child in enumerate(value):
                walk(child, f"{prefix}{sep}{index}")
        else:
            flat[prefix] = value

    for key, value in data.items():
        walk(value, key)
    return flat

# Complexity: O(N) time and space for a document with N values in total.
# Recursion depth equals the nesting depth; JSON from a config API is
# shallow. For deeply nested input, replace the recursion with an explicit
# stack of (prefix, value) pairs.
# `and value` sends empty containers to the else branch, so they become
# leaves instead of disappearing.
# Walking the top-level items separately means every call to walk() already
# has a prefix, so no "is this the top?" check is needed (such a check would
# mishandle a key that is the empty string).
# Alternative: a generator that yields (path, leaf) pairs, then dict(...)
# over it; same cost, easier to reuse for printing key=value lines.
