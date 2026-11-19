"""Count values in a range with bisect (drill, 5 to 8 minutes).

A sorted list holds the start times of all builds of the day (seconds since
midnight). Answer "how many builds started between lo and hi, both ends
included?" without scanning the list.

Input
    values: a list of ints sorted ascending. Duplicates are allowed.
    lo, hi: the range limits, both inclusive.

Output
    An int: how many v in values satisfy lo <= v <= hi.
    Return 0 when lo > hi.

Constraints
    len(values) <= 10**6, and the function is called many times, so each
    call must be O(log n). A loop over values is too slow.

Example 1
    count_in_range([1, 3, 3, 5, 8, 13], 3, 8)   ->  4      (3, 3, 5, 8)

Example 2
    count_in_range([1, 3, 3, 5, 8, 13], 4, 4)   ->  0

Example 3
    count_in_range([], 0, 10)                   ->  0
    count_in_range([5], 10, 1)                  ->  0      (lo > hi)
"""


def count_in_range(values: list[int], lo: int, hi: int) -> int:
    """Return how many values v satisfy lo <= v <= hi (values is sorted)."""
    raise NotImplementedError
