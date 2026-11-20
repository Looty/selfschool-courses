---
id: l01
title: "The Python you type from memory"
quiz: quiz-01.yaml
resources: [../resources/ch01/top_k_frequent_starter.py, ../resources/ch01/top_k_frequent_solution.py, ../resources/ch01/top_k_frequent_test.py, ../resources/ch01/group_anagrams_starter.py, ../resources/ch01/group_anagrams_solution.py, ../resources/ch01/group_anagrams_test.py]
sources: [1, 3, 8, 9, 12, 14, 15, 16]
---
After this lesson you can solve most timed problems with six plain-Python patterns, name the library shortcut for each, and spot the classic bugs when you read someone else's code.

## Plain Python is enough

Loops, `dict`, `list`, `set`, `sorted(key=)` and `str.split` solve almost every timed problem. Library helpers are shortcuts. If you forget one, write the three lines yourself and say so: "I'd use `Counter` here; I'll write the dict version."

## The routine in a bare editor

1. **Restate and ask:** sizes, duplicates, empty input, output order.
2. **Two examples:** one normal, one edge (empty, ties), as comments.
3. **Brute force and its cost:** "nested loop, O(n**2), too slow for 10**5." Python gets 10 seconds [1].
4. **Code, then test with prints:** trace your two examples, state time and space.

Check the version first with `import sys; print(sys.version)` [3].

## Six patterns

**1. Count with a dict.**

```python
counts = {}
for x in items:
    counts[x] = counts.get(x, 0) + 1     # get never raises KeyError
```

Shortcut: `Counter(items)`; `most_common(k)` keeps ties in first-seen order, not alphabetical [9] [15].

**2. Group into a dict of lists.**

```python
groups = {}
for w in words:
    groups.setdefault("".join(sorted(w)), []).append(w)
```

Shortcut: `groups = defaultdict(list)`, then `groups[key].append(w)` [9] [15].

**3. Sort by a tuple key.**

```python
ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
```

Count descending, name ascending. Sorts are stable; `sort()` returns `None`, `sorted()` returns a new list [12] [15].

**4. Sliding window.**

```python
window = best = sum(nums[:k])            # start from a real window, not 0
for i in range(k, len(nums)):
    window += nums[i] - nums[i - k]
    best = max(best, window)
```

Add one item, drop one: O(n). Starting `best` at 0 fails on all-negative input.

**5. Sort, then merge intervals.**

```python
merged = []
for start, end in sorted(intervals):
    if merged and start <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    else:
        merged.append((start, end))
```

`max` keeps a nested interval from shrinking the merged one [12].

**6. A queue, or top-k.**

```python
q = deque([start])
while q:
    node = q.popleft()                   # list.pop(0) is O(n)
    q.extend(next_nodes(node))
```

`deque` ends are about O(1); a list pays O(n) at the front [9] [14]. For top-k, `heapq.heappush(h, x)` / `heappop(h)` keep the smallest at `h[0]`, and `heapq.nsmallest(k, data, key=...)` equals a sort plus a slice [8]. `sorted(...)[:k]` is fine when you forget it.

## Built-ins to type blind

```python
for i, x in enumerate(xs, start=1):     # index and value
for a, b in zip(xs, ys):                # stops at the shorter
"  a  b ".split()                       # ['a', 'b']; split(",") keeps empties
",".join(parts)                         # all items must be str
line.strip()                            # both ends
```

`max(xs)` on an empty list raises `ValueError` without `default` [16].

## Reading and reviewing code

When asked to explain or review, check these first:

- **Off-by-one.** Does `range` include the last index? Two `bisect_left` calls for a closed range drop values equal to `hi`.
- **Mutable default argument.** `def f(x, acc=[])` shares one list across calls. Use `acc=None` and create the list inside.
- **Changing a container while looping over it.** A dict can raise `RuntimeError` [15]; loop over a copy, `list(d)`.
- **`return` inside the loop.** A `return` that should come after the loop exits on the first item. Check indentation.
- **Shared inner lists.** `dict.fromkeys(keys, [])` and `[[]] * 3` share one list [15].

## Exercises

Edit the starter, run `python name_test.py`, then `python name_test.py name_solution` to check the reference. Write the plain-dict version first, then read the solution.

1. **`top_k_frequent`** (20 minutes). Count, then pick `k` with key `(-count, name)`. Mistake: `most_common` breaks ties in the wrong order [9].
2. **`group_anagrams`** (20 minutes). Key each word by `"".join(sorted(word))`, return the groups in first-seen order. Dicts keep insertion order, so no final sort is needed [15].

:::key-takeaways
- Plain loops and dicts first; name the shortcut, and write it out if you forget it.
- Count with `get`, group with `setdefault`, rank with a `(-count, name)` key. [12] [15]
- Use a `deque` for queues and a heap or `sorted(...)[:k]` for top-k. [8] [9]
- When reviewing, check ranges, mutable defaults, loop mutation and early `return`. [15]
:::

:::glossary
- **Brute force**: the obvious solution that tries everything, usually slow.
- **Sliding window**: a fixed-length stretch of a sequence that moves one step at a time.
- **Stable sort**: a sort that keeps equal items in their original order.
- **Heap**: a list arranged so that the smallest item is always at index 0.
:::
