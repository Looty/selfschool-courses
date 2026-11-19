---
id: l03
title: "Sorting, heaps, bisect and itertools"
quiz: quiz-03.yaml
resources: [../resources/ch02/top_k_frequent_starter.py, ../resources/ch02/top_k_frequent_solution.py, ../resources/ch02/top_k_frequent_test.py, ../resources/ch02/merge_sorted_streams_starter.py, ../resources/ch02/merge_sorted_streams_solution.py, ../resources/ch02/merge_sorted_streams_test.py, ../resources/ch02/count_in_range_starter.py, ../resources/ch02/count_in_range_solution.py, ../resources/ch02/count_in_range_test.py]
sources: [8, 10, 11, 12, 13, 14, 16, 20, 22]
---
After this lesson you can sort by several keys, keep a top-k with a heap, answer range questions with `bisect`, and use the main `itertools` and `functools` tools without looking at the documentation.

## Sorting

`sorted(xs)` returns a new list and accepts any iterable; `xs.sort()` sorts in place and returns `None`. Both take `key=` and `reverse=`, and the key function is called once per item. [12] Sorts are stable: items with equal keys keep their original order, also with `reverse=True`. [12] `list.sort()` is O(n log n) in the worst case and O(n) on input that is already ordered. [14]

```python
words = ["b10", "a2", "a10"]
sorted(words, key=lambda s: (s[0], -int(s[1:])))   # ['a10', 'a2', 'b10']
sorted(pairs, key=lambda p: (-p[1], p[0]))         # count desc, name asc
from operator import itemgetter
sorted(rows, key=itemgetter(1, 2))                 # two-level key [12]
```

A tuple key compares left to right, so negating a number gives "descending on this field, ascending on the next". For strings that cannot be negated, sort twice: secondary key first, then primary key, relying on stability. [12] For an old comparison function that returns negative, zero or positive, wrap it with `functools.cmp_to_key`. [11] Sorting a list that contains `None` and numbers raises `TypeError`. [12]

## Heaps

A heap is a plain list kept so that `heap[0]` is the smallest item. [8]

```python
import heapq
h = [5, 1, 4]
heapq.heapify(h)            # in place, linear time
heapq.heappush(h, 2)
heapq.heappop(h)            # smallest; IndexError on an empty heap
heapq.heappushpop(h, 3)     # push then pop, cheaper than two calls
heapq.nsmallest(2, data, key=len)   # same as sorted(data, key=len)[:2]
```

`heapq` compares with `<` only. [8] `nlargest` and `nsmallest` are equivalent to a sort and a slice and are best for small `n`; for `n == 1` use `max` or `min`, and for large `n` use `sorted`. [8]

For a max-heap on Python 3.14 and later there are `heappush_max`, `heappop_max` and related functions. [8] [22] They do not exist on 3.11, so the portable trick is to push the negated number.

**Ties.** Pushing `(priority, task)` fails when two priorities tie and the tasks cannot be compared. Add a counter in the middle, `(priority, next(counter), task)`, or compare on a field only. [8]

```python
heapq.heappush(h, (1, {"vm": "a"}))
heapq.heappush(h, (1, {"vm": "b"}))   # TypeError: '<' not supported ... 'dict'
```

`heapq.merge(*sorted_inputs, key=None)` merges inputs that are already sorted and returns an iterator. [8]

## bisect

On a sorted list, `bisect_left(a, x)` returns the insertion point before equal items, and `bisect_right(a, x)` (alias `bisect`) the one after them. [13]

```python
from bisect import bisect_left, bisect_right, insort
a = [1, 3, 3, 5, 8]
bisect_left(a, 3), bisect_right(a, 3)    # (1, 3)
bisect_right(a, 8) - bisect_left(a, 3)   # items in [3, 8] -> 4
insort(a, 4)                             # keeps order; search O(log n), insert O(n)
```

`bisect` finds a position and never calls `__eq__`. [13] The `key` argument (3.10+) is applied to the list items, not to `x`. [13] `insort` is dominated by its O(n) insertion step. [13]

## itertools

All return lazy iterators; wrap in `list()` to see them. [10]

```python
from itertools import chain, groupby, islice, product, permutations, combinations, accumulate, pairwise, zip_longest
list(chain("ab", "cd"))                  # a b c d
list(islice("ABCDE", 1, 3))              # B C   no negative indexes
list(product("AB", repeat=2))            # AA AB BA BB
list(permutations("ABC", 2))             # 6 ordered pairs
list(combinations("ABC", 2))             # AB AC BC
list(accumulate([1, 2, 3]))              # 1 3 6
list(pairwise([1, 5, 9]))                # (1, 5) (5, 9)  needs 3.10+
list(zip_longest("ab", "x", fillvalue="-"))
```

`groupby` starts a new group whenever the key changes, like Unix `uniq`, so it normally needs input sorted on the same key; each group is invalidated when `groupby` advances, so store it with `list(g)`. [10] `batched(iterable, n)` was added in 3.12, and its `strict` option in 3.13, so it is not available on 3.11. [10]

## functools and generators

```python
from functools import cache, lru_cache, partial, reduce

@cache                       # unbounded memo, 3.9+
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
partial(int, base=2)("101")  # 5
reduce(lambda acc, v: acc * v, [1, 2, 3, 4], 1)   # 24
```

`cache` is `lru_cache(maxsize=None)`; arguments must be hashable, so pass a tuple, not a list. [11] Do not cache impure functions. [11] `reduce` with an `initial` value returns it for an empty input. [11]

A generator function uses `yield`, keeps its state between calls and ends with `StopIteration`; a generator expression `(x * x for x in xs)` is more memory friendly than a list comprehension. [20] `next(it, default)` returns the default when the iterator is exhausted instead of raising. [16]

## Drills

Edit the starter and run `python name_test.py`; add the argument `name_solution` to test the reference. In the course's test run every solution passed on Python 3.13 and 3.11 and every starter failed with `NotImplementedError`.

1. **`top_k_frequent`** (8 minutes, 10 tests). Hint: count with `Counter`, then pick `k` with a key that makes ties alphabetical. Walkthrough: `heapq.nsmallest(k, counts.items(), key=lambda p: (-p[1], p[0]))`, O(n + m log k); `sorted(...)[:k]` is the simpler alternative when `k` is close to `m`. Mistake: `nlargest` with `(count, name)` returns tied names in reverse order.
2. **`merge_sorted_streams`** (8 minutes, 11 tests). Hint: keep one entry per stream in a heap. Walkthrough: push `(timestamp, stream_index, message)`, pop, then push the next item of the same stream; the stream index is the tie-breaker so messages are never compared; O(n log s). `heapq.merge(*streams, key=...)` is the one-line alternative, and it also passed the tests. Mistake: concatenating and sorting loses the O(log s) behaviour.
3. **`count_in_range`** (5 minutes, 11 tests). Hint: two bisect calls. Walkthrough: `bisect_right(a, hi) - bisect_left(a, lo)`, O(log n), after a guard for `lo > hi`. Mistake: using `bisect_left` for both ends drops values equal to `hi`.

## Gotchas

- **Using `groupby` on unsorted data.** You get one group per run, not per key. [10] Sort first.
- **Comparing unorderable heap items.** Equal priorities fall through to the payload. [8] Add a tie-breaker.
- **`heappush_max` on an older Python.** It is new in 3.14. [22]
- **`sort()` returned `None`.** `xs = xs.sort()` throws the list away. [12]
- **A list argument to a cached function.** Lists are not hashable. [11] Pass a tuple.
- **`insort` in a hot loop.** Each call costs O(n). [13] Collect, then sort once.

:::key-takeaways
- Sorts are stable; use tuple keys, negating numbers, for mixed directions. [12]
- A heap is a list; `heap[0]` is the minimum; add a tie-breaker to tuples. [8]
- `bisect_right(hi) - bisect_left(lo)` counts a closed range in O(log n). [13]
- `groupby` needs sorted input; `batched` needs 3.12; max-heap functions need 3.14. [10] [22]
- `cache` needs hashable arguments. [11]
:::

:::glossary
- **Stable sort**: a sort that keeps equal items in their original order.
- **Heap**: a list arranged so that the smallest item is always at index 0.
- **Priority queue**: a queue where the item with the best priority leaves first.
- **Tie-breaker**: an extra field that decides the order when the main keys are equal.
- **Insertion point**: the index where a value would go to keep a sorted list sorted.
- **Lazy iterator**: an object that produces items one at a time, only when asked.
- **Memoisation**: remembering the result of a call so the same call is not computed twice.
- **Generator**: a function that yields values one by one and remembers where it stopped.
:::
