---
id: l08
title: "Exercise: build dependency order"
quiz: quiz-03.yaml
resources: [../resources/ch03/build_order_starter.py, ../resources/ch03/build_order_solution.py, ../resources/ch03/build_order_test.py]
sources: [9, 34]
---
After this lesson you can order build targets by their dependencies, group them into levels that can build in parallel, report a cycle by name, and show the same result with `graphlib.TopologicalSorter`.

## Shortcut

Download the three `build_order_*.py` files into one folder:

```bash
python build_order_test.py                    # your starter
python build_order_test.py build_order_solution
```

In the course's test run the reference printed `Ran 9 tests` and `OK` on Python 3.13 and 3.11. The untouched starter printed `FAILED (errors=9)`, all `NotImplementedError`. The test file also runs the `graphlib` version when your module defines `build_order_graphlib`.

## The problem (25 minutes)

`deps` maps a target to the targets it depends on: `{"app": ["libnet", "libjson"], "libnet": ["libc"], "libjson": ["libc"], "tests": ["app"]}`. Return `(order, levels)`. `levels` is a list of lists, each sorted by name: level 0 has every target with no dependencies, level k holds targets whose dependencies are all in earlier levels. Targets in one level can build in parallel. `order` is the levels concatenated. For the example, `levels == [["libc"], ["libjson", "libnet"], ["app"], ["tests"]]`. A cycle raises `ValueError("dependency cycle: a -> b -> c -> a")`.

**Questions worth asking:** Can a name appear only as a dependency (yes: it is a target with none)? Are duplicate dependencies possible? What does a self-dependency mean? If there are several cycles, must I report a particular one? Is the order inside a level fixed?

## Hints

1. Normalise first: every name mentioned, as a key or as a dependency, becomes a node.
2. Count each node's unmet dependencies (its in-degree). Nodes at zero are ready.
3. Process one whole level at a time: everything ready now is a level; finishing it lowers the counts of the targets waiting on it.
4. If fewer nodes were built than exist, the rest are stuck behind a cycle. Walk the stuck nodes to find the loop.

## Walkthrough: Kahn's algorithm by hand

Kahn's algorithm repeatedly removes nodes that have no unmet dependencies. The `deque` from `collections` supports O(1) appends and pops at both ends [9], which is why it, not a list with `pop(0)`, is the usual queue.

```python
def build_order(deps):
    graph = _normalise(deps)                       # name -> set of dependencies
    indegree = {t: len(needs) for t, needs in graph.items()}
    dependents = defaultdict(list)                 # dependency -> targets waiting
    for target, needs in graph.items():
        for name in needs:
            dependents[name].append(target)

    ready = deque(sorted(t for t, n in indegree.items() if n == 0))
    levels = []
    while ready:
        level = list(ready)
        levels.append(level)
        ready.clear()
        unblocked = []
        for done in level:
            for target in dependents[done]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    unblocked.append(target)
        ready.extend(sorted(unblocked))
    if sum(map(len, levels)) < len(graph):
        stuck = {t for t, n in indegree.items() if n > 0}
        raise ValueError("dependency cycle: " + " -> ".join(_find_cycle(graph, stuck)))
    return [t for level in levels for t in level], levels
```

A target enters a level only when its last dependency finished, so its level is the length of the longest dependency chain beneath it, not the first time it was seen. Using sets in `_normalise` makes duplicate dependencies count once.

**Naming the cycle.** Every node left with a positive in-degree still depends on another stuck node, so following one dependency at a time must eventually repeat a name. `_find_cycle` starts at the smallest stuck name, records each position and stops at the first repeat, then returns the loop `a -> b -> c -> a`. Nodes that merely depend on a cycle are stuck too, but the walk never ends in them: it always continues to a node that is itself in a cycle.

**Complexity.** V targets, E dependency edges: O(V + E) for Kahn's algorithm, O(V log V) extra for sorting within levels, O(V + E) space. Alternative: depth-first search with three states (new, in progress, done) detects a cycle when it meets an in-progress node and gives an order by reverse finishing time, but it does not hand you the levels as directly.

## The library answer: graphlib

`graphlib.TopologicalSorter(graph)` takes a dict whose values are the **predecessors** of each key, the things it depends on and that must come first [34]. That is the same shape as `deps`.

```python
from graphlib import CycleError, TopologicalSorter

ts = TopologicalSorter(deps)
print(tuple(ts.static_order()))     # a valid order
```

`static_order()` returns an iterator over nodes in a topological order and raises `CycleError` if there is a cycle; do not call `prepare()` or `done()` when using it [34]. For levels, use the three-step protocol: `prepare()` checks for cycles, then loop while `is_active()`, take `get_ready()` (a tuple of all nodes now ready), build them, and call `done(*nodes)` [34].

```python
ts = TopologicalSorter(deps)
ts.prepare()
levels = []
while ts.is_active():
    group = sorted(ts.get_ready())
    levels.append(group)
    ts.done(*group)
```

On a cycle, `prepare()` raises `CycleError`, a subclass of `ValueError`; the cycle is the second element of its `args`, a list in which each node is an immediate predecessor of the next and the first and last node are equal [34]. Because each node is a predecessor (dependency) of the next, the list reads backwards compared with "depends on", so the reference reverses it. A name that appears only as a predecessor is added automatically with no predecessors of its own [34]. Calling `get_ready()` on a graph with a cycle can still return the nodes that are not blocked [34].

## Gotchas

- **Direction of the edge.** In `graphlib` the dict maps a node to what must come before it. Passing "who depends on me" produces a valid but reversed order. [34]
- **Dependencies that are not keys.** `deps["app"] = ["libc"]` with no `"libc"` key must still create the node, or `indegree["libc"]` raises `KeyError`. [34]
- **`list.pop(0)` as a queue.** It moves every element; use `deque.popleft()`. [9]
- **Calling `prepare()` with `static_order()`.** `static_order()` does it for you. [34]
- **Reporting the wrong thing as the cycle.** The stuck set includes nodes that only depend on a cycle; walk dependencies to the first repeated name rather than printing the stuck set.
- **Assuming one valid order.** Several orders are valid; the exact order from `static_order()` can depend on insertion order. [34] Test validity, or sort inside levels, instead of comparing to one hard-coded order.

## Follow-up variation

Each target has a build time and you have four workers. Now the useful number is the critical path, the longest chain by total time, and a worker pool pulls ready targets as soon as a dependency finishes rather than level by level. This is the pattern in the `graphlib` docs: put ready nodes on a queue, let workers finish them, call `done(node)` and ask `get_ready()` again [34]. Discuss why strict levels waste time when a short target waits for a long one in its level.

:::key-takeaways
- Kahn's algorithm: in-degree counts, a `deque` of ready nodes, process, decrement, repeat; leftovers mean a cycle. [9]
- Process whole levels to get parallel groups; a node's level is its longest chain depth.
- `TopologicalSorter` takes node to predecessors; `static_order()` for an order, `prepare`/`get_ready`/`done` for groups. [34]
- `CycleError` is a `ValueError`; its second argument is the cycle. [34]
:::

:::glossary
- **Topological order**: an ordering where every target comes after everything it depends on.
- **In-degree**: the number of unmet dependencies a target still has.
- **Kahn's algorithm**: a method that repeatedly builds the targets whose in-degree is zero.
- **deque**: a double-ended queue with fast appends and pops at both ends.
- **Cycle**: a chain of dependencies that leads back to where it started, so no valid order exists.
- **Critical path**: the longest chain of dependent steps, which sets the minimum total time.
:::
