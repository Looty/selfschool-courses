"""Exercise: merge reservations and find the peak (time box: 12 minutes).

Each VM reservation is a pair (start, end) of integers (for example minutes
since midnight) with start < end. A reservation covers the half-open range
[start, end): it includes `start` and stops just before `end`.

1. merge_reservations(reservations) -> list of (start, end)
   Return the busy periods: the reservations merged so that no two periods in
   the result overlap or touch, sorted by start. Two reservations that touch
   ((1, 5) and (5, 8)) form one busy period (1, 8).

2. peak_concurrency(reservations) -> int
   Return the largest number of VMs running at the same moment. Because ranges
   are half-open, a VM that ends at 5 and one that starts at 5 are NOT running
   at the same moment.

Both functions:
  * accept the reservations in any order and must not modify the input list
  * return [] and 0 for an empty list
  * raise ValueError if any reservation has end <= start

Examples:

    merge_reservations([(1, 5), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]
    merge_reservations([(5, 8), (1, 5)])          == [(1, 8)]
    peak_concurrency([(1, 5), (2, 6), (8, 10)])   == 2
    peak_concurrency([(1, 5), (5, 8)])            == 1

Check your work:  python merge_reservations_test.py
"""


def merge_reservations(reservations):
    """Return the merged busy periods as a list of (start, end), sorted by start."""
    raise NotImplementedError


def peak_concurrency(reservations):
    """Return the largest number of reservations active at the same moment."""
    raise NotImplementedError
