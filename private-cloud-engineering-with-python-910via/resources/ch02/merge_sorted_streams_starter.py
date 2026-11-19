"""Merge sorted log streams (drill, 5 to 8 minutes).

Each hypervisor produces a log that is already sorted by timestamp. Merge
several such logs into one list sorted by timestamp.

Input
    streams: a list of streams. Each stream is a list of
             (timestamp, message) tuples, sorted by timestamp ascending.
             timestamp is an int (seconds), message is a str.
             A stream may be empty, and the list of streams may be empty.

Output
    One list of (timestamp, message) tuples, sorted by timestamp ascending.
    When timestamps are equal, the entry from the stream with the lower
    index comes first, and entries of one stream keep their order.

Constraints
    Total number of entries n <= 10**6, number of streams s <= 1000.
    Aim for O(n log s): do not concatenate and sort everything.
    Messages must never be compared with each other.

Example 1
    merge_sorted_streams([
        [(1, "a1"), (4, "a2")],
        [(2, "b1"), (3, "b2"), (9, "b3")],
    ])
    -> [(1, "a1"), (2, "b1"), (3, "b2"), (4, "a2"), (9, "b3")]

Example 2 (equal timestamps: stream 0 before stream 1)
    merge_sorted_streams([[(5, "x")], [(5, "w")]])  ->  [(5, "x"), (5, "w")]

Example 3
    merge_sorted_streams([])  ->  []
"""


def merge_sorted_streams(streams: list[list[tuple[int, str]]]) -> list[tuple[int, str]]:
    """Merge streams sorted by timestamp into one sorted list."""
    raise NotImplementedError
