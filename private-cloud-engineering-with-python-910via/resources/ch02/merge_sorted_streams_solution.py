"""Reference solution for merge_sorted_streams (see the starter file)."""
import heapq


def merge_sorted_streams(streams: list[list[tuple[int, str]]]) -> list[tuple[int, str]]:
    """Merge streams sorted by timestamp into one sorted list."""
    iterators = [iter(stream) for stream in streams]
    heap = []
    for index, iterator in enumerate(iterators):
        first = next(iterator, None)
        if first is not None:
            heap.append((first[0], index, first[1]))
    heapq.heapify(heap)

    merged = []
    while heap:
        timestamp, index, message = heapq.heappop(heap)
        merged.append((timestamp, message))
        following = next(iterators[index], None)
        if following is not None:
            heapq.heappush(heap, (following[0], index, following[1]))
    return merged

# Complexity: O(n log s) time for n entries in s streams (the heap never
# holds more than one entry per stream), O(s) extra space plus the output.
# The stream index is the tie-breaker: the heap holds at most one entry per
# stream, so (timestamp, index) is unique and the message in third place is
# never compared.
# Alternative: list(heapq.merge(*streams, key=lambda entry: entry[0])).
# It is one line and lazy; in the course's test run it passed the same tests,
# including the equal-timestamp cases.
