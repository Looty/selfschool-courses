"""Exercise: build dependency order (time box: 25 minutes).

A build system knows, for each target, which targets it depends on:

    deps = {
        "app":    ["libnet", "libjson"],
        "libnet": ["libc"],
        "libjson": ["libc"],
        "tests":  ["app"],
    }

A target may only be built after every target it depends on. A name that
appears only as a dependency (here "libc") is a target with no dependencies.

Write build_order(deps) that returns a pair (order, levels):

    levels  list of lists. levels[0] holds every target with no dependencies;
            levels[k] holds every target whose dependencies are all in
            levels[0..k-1] and that is not in an earlier level. Targets in one
            level can build in parallel. Each level is sorted by name.
    order   one valid build order: the levels concatenated, in level order.

For the example above:

    levels == [["libc"], ["libjson", "libnet"], ["app"], ["tests"]]
    order  == ["libc", "libjson", "libnet", "app", "tests"]

If the dependencies contain a cycle (including a target that depends on
itself), raise ValueError with a message of the form

    "dependency cycle: a -> b -> c -> a"

where each name depends on the next one and the first and last names are the
same. When several cycles exist, report any one of them.

Duplicate names in a dependency list count once. An empty dict gives ([], []).

Check your work:  python build_order_test.py
"""


def build_order(deps):
    """Return (order, levels) for a dict of target -> iterable of dependencies."""
    raise NotImplementedError
