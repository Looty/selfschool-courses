"""Reference solution for the build order exercise (see build_order_starter.py)."""
from collections import defaultdict, deque
from graphlib import CycleError, TopologicalSorter


def _normalise(deps):
    """Return target -> set of dependencies, with every mentioned name as a key."""
    graph = {target: set(needs) for target, needs in deps.items()}
    for needs in list(graph.values()):
        for name in needs:
            graph.setdefault(name, set())
    return graph


def _find_cycle(graph, stuck):
    """Follow dependencies inside `stuck` until a name repeats; return that loop."""
    node = min(stuck)
    path, seen_at = [], {}
    while node not in seen_at:
        seen_at[node] = len(path)
        path.append(node)
        node = min(d for d in graph[node] if d in stuck)   # every stuck node has one
    return path[seen_at[node]:] + [node]


def build_order(deps):
    """Kahn's algorithm, one level at a time."""
    graph = _normalise(deps)
    indegree = {target: len(needs) for target, needs in graph.items()}
    dependents = defaultdict(list)                  # dependency -> targets waiting on it
    for target, needs in graph.items():
        for name in needs:
            dependents[name].append(target)

    ready = deque(sorted(t for t, n in indegree.items() if n == 0))
    levels = []
    while ready:
        level = list(ready)                         # everything ready now builds in parallel
        levels.append(level)
        ready.clear()
        unblocked = []
        for done in level:
            for target in dependents[done]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    unblocked.append(target)
        ready.extend(sorted(unblocked))

    built = sum(len(level) for level in levels)
    if built < len(graph):
        stuck = {t for t, n in indegree.items() if n > 0}
        cycle = _find_cycle(graph, stuck)
        raise ValueError("dependency cycle: " + " -> ".join(cycle))
    order = [target for level in levels for target in level]
    return order, levels


def build_order_graphlib(deps):
    """The library answer: graphlib.TopologicalSorter takes target -> predecessors directly."""
    sorter = TopologicalSorter(deps)
    try:
        sorter.prepare()
    except CycleError as exc:
        # args[1] lists each node as a predecessor (dependency) of the next one, so reverse it
        # to read "depends on" from left to right.
        cycle = list(reversed(exc.args[1]))
        raise ValueError("dependency cycle: " + " -> ".join(cycle)) from exc
    levels = []
    while sorter.is_active():
        group = sorted(sorter.get_ready())
        levels.append(group)
        sorter.done(*group)
    return [t for level in levels for t in level], levels


# Complexity for V targets and E dependency edges: O(V + E) for Kahn's algorithm itself, plus
# O(V log V) for sorting names inside levels; O(V + E) space for the in-degree and dependents
# maps. Finding the cycle walks at most V nodes.
# Alternative: depth-first search with three colours (unvisited, in progress, done) gives a
# reverse post-order and finds a cycle when it meets an "in progress" node, but it does not
# produce the parallel levels as directly as Kahn's algorithm does.
