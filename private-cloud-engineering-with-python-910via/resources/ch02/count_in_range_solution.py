"""Reference solution for count_in_range (see count_in_range_starter.py)."""
from bisect import bisect_left, bisect_right


def count_in_range(values: list[int], lo: int, hi: int) -> int:
    """Return how many values v satisfy lo <= v <= hi (values is sorted)."""
    if lo > hi:
        return 0
    first = bisect_left(values, lo)     # index of the first value >= lo
    after = bisect_right(values, hi)    # index just past the last value <= hi
    return after - first

# Complexity: O(log n) time per call, O(1) extra space.
# bisect_left for the lower limit and bisect_right for the upper limit make
# both ends inclusive. Swapping them drops every value equal to lo or hi.
# Without the lo > hi guard the subtraction can go negative:
# count_in_range([5], 10, 1) would give 0 - 1 = -1.
# Alternative for an unsorted list queried once: sum(lo <= v <= hi for v in
# values), O(n) per query. With many queries, sort once (O(n log n)) and
# bisect each time.
