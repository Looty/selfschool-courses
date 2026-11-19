---
id: l02
title: "Built-in types and collections"
quiz: quiz-02.yaml
resources: [../resources/ch02/group_anagrams_starter.py, ../resources/ch02/group_anagrams_solution.py, ../resources/ch02/group_anagrams_test.py, ../resources/ch02/first_unique_char_starter.py, ../resources/ch02/first_unique_char_solution.py, ../resources/ch02/first_unique_char_test.py, ../resources/ch02/sliding_window_max_sum_starter.py, ../resources/ch02/sliding_window_max_sum_solution.py, ../resources/ch02/sliding_window_max_sum_test.py]
sources: [9, 14, 15, 16, 18]
---
After this lesson you can type the everyday string, list, dict and set methods from memory, say what each costs, and reach for `Counter`, `defaultdict`, `deque` and `namedtuple` without looking them up.

## Strings

Strings are immutable: every method returns a new string. [15]

```python
"a,b,,c".split(",")        # ['a', 'b', '', 'c']  separators are not merged
"  a   b ".split()         # ['a', 'b']  no argument: runs of whitespace, no empties
"k=v=w".partition("=")     # ('k', '=', 'v=w'); not found gives (s, '', '')
",".join(["a", "b"])       # 'a,b'  TypeError if any item is not a str
"  x \n".strip()           # 'x'   strip(chars) removes a SET of characters
"Test_a".removeprefix("Test_")   # 'a'  (3.9+)
"abc".startswith(("ab", "x"))    # True: a tuple tries several prefixes
"abc".find("z")            # -1      "abc".index("z") raises ValueError
"42".isdigit()             # True; "-42".isdigit() is False
f"{3.14159:.2f} {'vm':>5} {7:03d}"   # '3.14    vm 007'
```

`split`, `partition`, `join`, `strip`, `startswith`, `find`, `index` and `isdigit` behave as shown. [15] Use `in` to test membership and `find` only when you need the position. [15] The f-string forms `{x:.2f}`, `{x!r}` and `{x=}` are in the tutorial. [18]

## Lists

`append`, `extend`, `insert`, `pop(i=-1)`, `remove`, `reverse`, `sort`, `copy`. `sort()` and `reverse()` return `None`; `sorted()` returns a new list. [15] Slices clamp out-of-range bounds instead of raising, while `s[i]` out of range raises `IndexError`. [15] `[[]] * 3` repeats one inner list three times; use `[[] for _ in range(3)]`. [15]

## Dicts and sets

```python
d.get(k, 0)             # never raises KeyError
d.setdefault(k, [])     # insert [] if missing, return the stored value
d.pop(k, None)          # remove, no error if absent
for k, v in d.items():  # insertion order is guaranteed since 3.7
{k: v for k, v in pairs}
```

Dict order is insertion order. [15] Views from `keys()`, `values()` and `items()` are live, and changing the dict size while iterating can raise `RuntimeError`. [15] `dict.fromkeys(keys, [])` shares one list between all keys. [15]

Sets hold hashable items. `|` union, `&` intersection, `-` difference, `^` symmetric difference; `add`, `discard` (no error) versus `remove` (`KeyError`). `{}` is an empty dict, so write `set()`. [15]

## What it costs

| Operation | list | dict / set | deque |
| --- | --- | --- | --- |
| `x in c` | O(n) [14] | O(1) average [14] | not covered by the sources |
| append at the end | O(1) amortized [14] | O(1) amortized [14] | about O(1) [9] |
| pop / insert at the front | O(n) [14] | n/a | about O(1) [9] |
| index in the middle | O(1) [14] | n/a | O(n) [9] |
| sort | O(n log n) [14] | n/a | n/a |

Dict and set figures assume a good hash; if every key collides each operation degrades to O(n). [14] Building a string with `+=` in a loop is quadratic; collect pieces and `"".join` them. [15]

## collections

```python
from collections import Counter, defaultdict, deque, namedtuple

c = Counter("abracadabra")       # missing keys read as 0
c.most_common(2)                 # [('a', 5), ('b', 2)]; ties keep first-seen order
Counter(a=3, b=1) - Counter(a=1, b=2)   # Counter({'a': 2}) keeps positives only

g = defaultdict(list)            # g[k] creates [] on first access
g["x"].append(1)

d = deque([1, 2, 3], maxlen=3)   # a full bounded deque drops from the other end
d.appendleft(0); d.popleft(); d.rotate(1)

Pt = namedtuple("Pt", "host cpu")
p = Pt("kvm", 4); p.cpu; p._replace(cpu=8); p._asdict()
```

`Counter` is a `dict` subclass; `update` adds counts instead of replacing them, and `most_common` returns `(element, count)` pairs. [9] `defaultdict` calls its factory only in `d[key]`; `d.get(key)` does not create an entry. [9] `deque` ends are about O(1); `popleft` and `appendleft` replace the O(n) `list.pop(0)` and `insert(0, x)`. [9] `namedtuple` instances are tuples with named fields, and `_replace` returns a new instance. [9] In `Counter`, the `^` operator is new in 3.15, so do not use it. [9]

## Built-ins to type blind

```python
enumerate(xs, start=1)   zip(a, b)   # zip stops at the shortest; strict=True raises
any(...)  all(...)       # any([]) is False, all([]) is True
min(xs, key=len)  max(xs, default=0)   # empty without default: ValueError
sum(xs)  divmod(17, 5)   # (3, 2); divmod(-17, 5) is (-4, 3)
sorted(xs, key=..., reverse=True)
```

All are in the built-ins reference; `max`/`min` return the first of tied items and raise `ValueError` on an empty iterable without `default`. [16]

## Drills

Each drill has a starter, a reference solution and a test file. Edit the starter, then run `python name_test.py`; run `python name_test.py name_solution` to test the reference. In the course's test run every solution passed its tests on Python 3.13 and 3.11 and every starter failed with `NotImplementedError`.

1. **`group_anagrams`** (6 minutes, 10 tests). Hint: a sorted word is the same for all anagrams; use it as a dict key. Walkthrough: `defaultdict(list)` keyed by `"".join(sorted(word))`, return `list(groups.values())`; O(n L log L). Mistake: forgetting that dicts keep first-seen order, then sorting needlessly.
2. **`first_unique_char`** (5 minutes, 10 tests). Hint: count first, then scan in order. Walkthrough: `Counter`, then `enumerate`; O(n). Mistake: `s.count(c)` inside the loop makes it O(n**2).
3. **`sliding_window_max_sum`** (8 minutes, 12 tests). Hint: when the window moves, add one item and subtract one. Walkthrough: sum the first `k`, then `window += nums[i] - nums[i-k]`; O(n). Mistake: starting `best` at 0 fails for all-negative input; alternative: a `deque(maxlen=k)`.

## Gotchas

- **`dict.fromkeys(keys, [])`.** All keys share one list. [15] Use a dict comprehension.
- **`pop(0)` in a loop.** Each call is O(n) on a list. [14] Use `deque.popleft()`. [9]
- **`strip("abc")` is not `removeprefix`.** `strip` removes any of the characters, from both ends. [15]
- **`Counter.most_common` on ties.** Equal counts keep first-seen order, not alphabetical. [9]
- **Mutating a dict while looping over it.** It can raise `RuntimeError` or skip entries. [15] Loop over `list(d)`.
- **`defaultdict` reads create keys.** `d[k]` inserts the default; `get` does not. [9]

:::key-takeaways
- `split()` with no argument drops empties; `split(",")` keeps them. [15]
- `x in list` is O(n); `x in set` or `dict` is O(1) on average. [14]
- Use `deque` for queues and `Counter` / `defaultdict` for counting and grouping. [9]
- `sort()` returns `None`; `sorted()` returns a list. [15]
- Check `k` against the list length and start maximums from the first value, not 0. [16]
:::

:::glossary
- **Immutable**: cannot be changed after creation, so every change makes a new object.
- **Amortized**: the average cost over many operations, even if a few are slower.
- **Hashable**: usable as a dict key or set member because it has a stable hash value.
- **Insertion order**: iterating a dict gives keys in the order they were first added.
- **Counter**: a dict subclass that counts hashable items.
- **defaultdict**: a dict that creates a missing value with a factory function on first access.
- **deque**: a double-ended queue with fast appends and pops at both ends.
- **namedtuple**: a tuple whose items also have names.
- **Sliding window**: a fixed-length stretch of a sequence that moves one step at a time.
:::
