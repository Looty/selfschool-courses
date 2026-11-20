"""Reference solution for the reservations exercise (see merge_reservations_starter.py)."""
import heapq


def _check(reservations):
    for start, end in reservations:
        if end <= start:
            raise ValueError(f"reservation ({start}, {end}) must have start < end")


def merge_reservations(reservations):
    """Return the merged busy periods as a list of (start, end), sorted by start."""
    _check(reservations)
    merged = []
    for start, end in sorted(reservations):          # sorted() copies; the input is untouched
        if merged and start <= merged[-1][1]:        # overlaps or touches the last period
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def peak_concurrency(reservations):
    """Return the largest number of reservations active at the same moment (sweep line)."""
    _check(reservations)
    events = []
    for start, end in reservations:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()        # at the same time, (t, -1) sorts before (t, 1): ends are applied first
    running = peak = 0
    for _time, delta in events:
        running += delta
        peak = max(peak, running)
    return peak


def peak_concurrency_heap(reservations):
    """Same answer with a min-heap of end times: the heap holds the VMs running right now."""
    _check(reservations)
    ends = []
    peak = 0
    for start, end in sorted(reservations):
        while ends and ends[0] <= start:             # everything that ended by `start` is gone
            heapq.heappop(ends)
        heapq.heappush(ends, end)
        peak = max(peak, len(ends))
    return peak


# Complexity for n reservations: all three functions sort, so O(n log n) time and O(n) space.
# The sweep is a single pass over 2n events; the heap version does at most n pushes and n pops.
# Alternative for small integer time ranges: a difference array (add 1 at start, subtract 1 at
# end, then take running sums) is O(n + T) for T time slots and needs no sort.
