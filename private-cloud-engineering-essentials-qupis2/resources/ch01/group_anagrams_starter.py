"""Group anagrams (drill, 5 to 8 minutes).

Two words are anagrams when they use the same letters the same number of
times, for example "listen" and "silent". Group the words of a list so that
each group holds words that are anagrams of each other.

Input
    words: a list of strings made of lower-case letters a-z. A word may be
           empty and may appear more than once.

Output
    A list of groups (lists of words).
    - Words keep their input order inside a group; duplicates are kept.
    - Groups are ordered by where their first word appears in the input.

Constraints
    len(words) <= 10**4, len(word) <= 100

Example 1
    group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    -> [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]

Example 2
    group_anagrams([])  ->  []

Example 3
    group_anagrams(["", "b", ""])  ->  [["", ""], ["b"]]
"""


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Return the words grouped by anagram class, in first-seen order."""
    raise NotImplementedError
