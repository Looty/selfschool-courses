"""Reference solution for sliding_window_max_sum (see the starter file)."""


def sliding_window_max_sum(nums: list[int], k: int) -> int:
    """Return the largest sum of k consecutive elements."""
    if k < 1 or k > len(nums):
        raise ValueError(f"window {k} does not fit a list of {len(nums)} items")
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best

# Complexity: O(n) time, O(k) extra space for the first slice (O(1) if the
# first window is summed with a loop).
# Start `best` from the first window, not from 0: with all-negative input
# the right answer is negative.
# Alternative for a stream that cannot be indexed: keep the window in
# collections.deque(maxlen=k). Before each append, subtract window[0] when
# the deque is full, then add the new value; the deque drops the oldest
# item by itself. Same O(n) time, O(k) space.
