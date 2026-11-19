"""Sliding window maximum sum (drill, 5 to 8 minutes).

A hypervisor reports one CPU sample per second. Find the busiest stretch of
k consecutive seconds: the largest sum of any k neighbouring samples.

Input
    nums: a list of integers (they may be negative).
    k:    the window length.

Output
    An int: the largest sum of k consecutive elements of nums.

Errors
    Raise ValueError when k < 1 or k > len(nums) (no window exists).

Constraints
    len(nums) <= 10**6. Summing every window from scratch is O(n * k) and
    too slow; keep a running sum instead.

Example 1
    sliding_window_max_sum([1, 4, 2, 10, 23, 3, 1, 0, 20], 4)  ->  39
    (the window 4, 2, 10, 23)

Example 2 (negative numbers: the answer is not 0)
    sliding_window_max_sum([-5, -2, -8], 2)  ->  -7

Example 3
    sliding_window_max_sum([7], 1)  ->  7
"""


def sliding_window_max_sum(nums: list[int], k: int) -> int:
    """Return the largest sum of k consecutive elements."""
    raise NotImplementedError
