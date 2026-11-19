"""First unique character (drill, 5 to 8 minutes).

Return the index of the first character that appears exactly once in a
string, or -1 when every character repeats.

Input
    s: a string (any characters; upper and lower case are different).

Output
    An int: the 0-based index of the first non-repeating character, or -1.

Constraints
    len(s) <= 10**5. One pass over the string plus one pass over the counts
    is expected; a nested loop over s is too slow at this size.

Example 1
    first_unique_char("swiss")  ->  1      ("w" is the first that occurs once)

Example 2
    first_unique_char("aabb")   ->  -1

Example 3
    first_unique_char("")       ->  -1
"""


def first_unique_char(s: str) -> int:
    """Return the index of the first character that occurs once, or -1."""
    raise NotImplementedError
