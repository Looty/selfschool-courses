---
id: l01
title: "The Python you type from memory"
quiz: quiz-01.yaml
resources: [../resources/ch01/top_k_frequent_starter.py, ../resources/ch01/top_k_frequent_solution.py, ../resources/ch01/top_k_frequent_test.py, ../resources/ch01/group_anagrams_starter.py, ../resources/ch01/group_anagrams_solution.py, ../resources/ch01/group_anagrams_test.py]
sources: [1, 8, 9, 12, 15]
---
Four tools solve most timed problems: count, group, sort with a key, take the top k.

**Routine in a bare editor.** (1) Ask about sizes, duplicates, empty input, output order. (2) Write a normal and an edge example as comments. (3) Name the slow obvious solution and its cost; Python gets 10 seconds [1]. (4) Code, trace both examples with `print`, state time and space.

## Counting: a tally sheet

**Rule:** a counting dict is a tally sheet: each item adds one tick next to its name, and a name not on the sheet counts as 0 [9].

```python
tally = {}
for level in ["ERR", "OK", "ERR"]:
    tally[level] = tally.get(level, 0) + 1
# {'ERR': 1} -> {'ERR': 1, 'OK': 1} -> {'ERR': 2, 'OK': 1}

from collections import Counter
tally = Counter(["ERR", "OK", "ERR"])   # Counter({'ERR': 2, 'OK': 1})
tally["WARN"]                           # 0, no error
Counter([])                             # Counter(): empty sheet
Counter(["b", "a", "b", "a", "c"]).most_common(2)   # [('b', 2), ('a', 2)]
```

Trap: `most_common` keeps ties first-seen, not alphabetical [9].

**Contrast:** `plain["ERR"] += 1` on an empty dict raises `KeyError`; on an empty `Counter` it works.

**P1.** What is `Counter("abcab").most_common(1)`?

## Grouping: labelled buckets

**Rule:** a dict of lists is a row of labelled buckets: compute the label, drop the item in that bucket; a new label creates its bucket [9].

```python
groups = {}
for word in ["eat", "tea", "tan"]:
    label = "".join(sorted(word))           # "eat" -> "aet"
    groups.setdefault(label, []).append(word)
# {'aet': ['eat']} -> {'aet': ['eat', 'tea']}
# -> {'aet': ['eat', 'tea'], 'ant': ['tan']}

from collections import defaultdict
buckets = defaultdict(list)                 # a missing label starts as []
buckets.get("xyz")                          # None, no bucket created
buckets["xyz"]                              # [], and now "xyz" is a key
```

`buckets[key]` creates the key; `get` does not [9]. Dicts keep insertion order [15].

**Contrast:** `dict.fromkeys` gives every key the same single list [15].

| Code, then `["a"].append("x")` | Result |
| --- | --- |
| `dict.fromkeys(["a", "b"], [])` | `{'a': ['x'], 'b': ['x']}` |
| `defaultdict(list)` | `{'a': ['x']}` |

**P2.** Bucket `["ab", "c", "de", "f"]` by `len(word)`. What is the dict?

## Sorting with a tuple key: dictionary order

**Rule:** the key turns each item into a tuple, and tuples compare left to right like words in a dictionary: the second field matters only when the first ties [12].

```python
pairs = [("c", 2), ("a", 3), ("b", 2)]                  # (name, count)
sorted(pairs, key=lambda pair: pair[1])                 # [('c', 2), ('b', 2), ('a', 3)]
sorted(pairs, key=lambda pair: -pair[1])                # [('a', 3), ('c', 2), ('b', 2)]
sorted(pairs, key=lambda pair: (-pair[1], pair[0]))     # [('a', 3), ('b', 2), ('c', 2)]
pairs.sort(key=lambda pair: pair[1])                    # None; pairs sorted in place
```

In rung two `c` stays before `b`: sorts are stable, so equal keys keep input order [12]. `sorted` returns a new list; `.sort()` returns `None` [12].

**Contrast:** `reverse=True` flips every field of the key. Same `pairs`:

| Key | Order | Ties |
| --- | --- | --- |
| `(-count, name)` | a, b, c | alphabetical |
| `count`, `reverse=True` | a, c, b | input order [12] |
| `(count, name)`, `reverse=True` | a, c, b | reverse alphabetical |

**P3.** What is `sorted([("x", 1), ("y", 3), ("z", 1)], key=lambda p: (-p[1], p[0]))`?

## Top k with heapq: keep the best few

**Rule:** a heap is a list that keeps its smallest item at index 0, and `heapq.nsmallest(k, data, key=...)` equals `sorted(data, key=...)[:k]` [8].

```python
import heapq
heap = [5, 1, 4]
heapq.heapify(heap)          # [1, 5, 4]; heap[0] == 1
heapq.heappush(heap, 2)      # heap[0] still 1
heapq.heappop(heap)          # 1; now heap[0] == 2
heapq.nsmallest(5, [3, 1])   # [1, 3]: k beyond the length returns everything
heapq.heappop([])            # IndexError
```

**Contrast:** `counts = {"b": 2, "a": 3, "c": 2}`, top 2 by count:

| Call | Result |
| --- | --- |
| `sorted(..., key=(-count, name))[:2]` | `[('a', 3), ('b', 2)]`, sorts everything |
| `nsmallest(2, ..., key=(-count, name))` | `[('a', 3), ('b', 2)]`, best for small k [8] |
| `nlargest(2, ..., key=(count, name))` | `[('a', 3), ('c', 2)]`, ties reversed |

**P4.** What is `heapq.nsmallest(2, [7, 3, 9, 3])`?

## Reviewing code

- **Mutable default:** `def f(x, acc=[])` shares one list across calls; use `acc=None`.
- **Shared lists:** `dict.fromkeys(keys, [])` and `[[]] * 3` [15].
- **Changing a dict while looping** can raise `RuntimeError`; loop over `list(d)` [15].

## Exercises

**`top_k_frequent`** and **`group_anagrams`**, 20 minutes each. Edit the starter, run `python name_test.py`, then read the solution and run `python name_test.py name_solution` (10 tests).

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `Counter(xs)` | tally; missing is 0 | `Counter("aba")["z"]` → `0` |
| `defaultdict(list)` | `d[k]` creates `[]` | `d["z"]` → `[]` |
| `sorted(xs, key=...)` | tuple keys left to right | `(-count, name)` → high first, then A to Z |
| `heapq.nsmallest(k, xs)` | `sorted(xs)[:k]` | `nsmallest(2, [7, 3, 9])` → `[3, 7]` |

## Answers

**P1.** `[('a', 2)]`: `a` and `b` tie at 2; `a` was seen first.

**P2.** `{2: ['ab', 'de'], 1: ['c', 'f']}`: label 2 appeared first.

**P3.** `[('y', 3), ('x', 1), ('z', 1)]`: highest count, then `x` before `z`.

**P4.** `[3, 3]`: duplicates are kept.

**R1.** An empty `Counter()`; any key reads as 0.

**R2.** `None`, and no key is added.

**R3.** `[('b', 2), ('a', 2)]`: the keys tie, so input order stays.

**R4.** `None`; `.sort()` works in place.

**R5.** `['a', 'b']`: the default list is created once.

**R6.** One, shared by both keys.

**R7.** `("b", 2)`: the name is flipped too.

## If you missed a quiz question

| If you thought... | Reread | Re-check |
| --- | --- | --- |
| A missing key or empty input raises | Counting | **R1.** What is `Counter([])`? |
| `get` creates the bucket | Grouping | **R2.** `defaultdict(list).get("k")`? |
| `fromkeys` gives each key its own list | Grouping | **R6.** `dict.fromkeys("xy", [])` holds how many lists? |
| Ties come out alphabetical | Sorting | **R3.** `sorted([("b", 2), ("a", 2)], key=lambda p: p[1])`? |
| `reverse=True` flips only the first field | Sorting | **R7.** Key `(count, name)`, `reverse=True`: `("a", 2)` or `("b", 2)` first? |
| `.sort()` returns the list | Sorting | **R4.** What does `pairs.sort()` return? |
| A default `[]` is fresh per call | Reviewing | **R5.** `def f(x, acc=[])` appends `x` and returns `acc`. `f("a")`, then `f("b")`? |

:::key-takeaways
- Count with `Counter`; group with `defaultdict(list)`. [9]
- Rank with `(-count, name)`; `reverse=True` flips every field. [12]
- Top k is `sorted(...)[:k]` or `heapq.nsmallest` with the same key. [8]
:::

:::glossary
- **Counter**: a dict that counts and reads a missing key as 0.
- **defaultdict**: a dict that creates a missing value when you read its key.
- **Stable**: keeps equal items in their original order.
- **Heap**: a list kept so the smallest item is at index 0.
- **Mutable default**: a default like `[]`, created once and shared by every call.
:::
