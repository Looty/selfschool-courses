"""Reference solution for first_unique_char (see first_unique_char_starter.py)."""
from collections import Counter


def first_unique_char(s: str) -> int:
    """Return the index of the first character that occurs once, or -1."""
    counts = Counter(s)
    for index, char in enumerate(s):
        if counts[char] == 1:
            return index
    return -1

# Complexity: O(n) time (one pass to count, one pass to find), O(u) space
# for u distinct characters.
# Slow version to avoid: `if s.count(char) == 1` inside the loop is O(n) per
# character, O(n**2) in total.
# Alternative: one pass that stores the first index of each character in a
# dict and marks repeats, then takes the minimum stored index. Same cost,
# and it works on a stream that can only be read once.
