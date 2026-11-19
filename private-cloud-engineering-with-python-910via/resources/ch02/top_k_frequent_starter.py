"""Top k frequent items with a heap (drill, 5 to 8 minutes).

A scheduler log holds one hypervisor name per placement failure. Report the
k hosts that fail most often, with their counts.

Input
    items: a list of strings (host names), in any order.
    k:     how many entries to return.

Output
    A list of (item, count) tuples, highest count first. Items with the same
    count are ordered alphabetically. If there are fewer than k distinct
    items, return all of them. Return [] when k <= 0.

Constraints
    len(items) <= 10**6, and k is usually much smaller than the number of
    distinct items. Aim for O(n + m log k) with m distinct items: do not
    sort all m of them.

Example 1
    top_k_frequent(["kvm-02", "kvm-01", "kvm-02", "kvm-03", "kvm-02", "kvm-01"], 2)
    -> [("kvm-02", 3), ("kvm-01", 2)]

Example 2 (tie on count 1: alphabetical order)
    top_k_frequent(["c", "a", "b"], 2)  ->  [("a", 1), ("b", 1)]

Example 3
    top_k_frequent([], 3)  ->  []
"""


def top_k_frequent(items: list[str], k: int) -> list[tuple[str, int]]:
    """Return the k most frequent items as (item, count), ties alphabetical."""
    raise NotImplementedError
