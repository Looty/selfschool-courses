"""Reference solution for top_k_frequent (see top_k_frequent_starter.py)."""
import heapq
from collections import Counter


def top_k_frequent(items: list[str], k: int) -> list[tuple[str, int]]:
    """Return the k most frequent items as (item, count), ties alphabetical."""
    if k <= 0:
        return []
    counts = Counter(items)
    return heapq.nsmallest(k, counts.items(), key=lambda pair: (-pair[1], pair[0]))

# Complexity: O(n) to count n items, then O(m log k) for nsmallest over the
# m distinct items, which keeps only k candidates at a time. Space O(m).
# Why nsmallest with a negated count: the wanted order is "count descending,
# name ascending". nlargest with key (count, name) would return ties in
# reverse alphabetical order.
# Alternative: sorted(counts.items(), key=lambda p: (-p[1], p[0]))[:k].
# It is O(m log m), simpler, and the better choice when k is close to m.
