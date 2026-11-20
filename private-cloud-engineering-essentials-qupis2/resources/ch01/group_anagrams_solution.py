"""Reference solution for group_anagrams (see group_anagrams_starter.py)."""
from collections import defaultdict


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Return the words grouped by anagram class, in first-seen order."""
    groups: dict[str, list[str]] = defaultdict(list)
    for word in words:
        signature = "".join(sorted(word))
        groups[signature].append(word)
    return list(groups.values())

# Complexity: O(n * L log L) time for n words of length up to L (sorting each
# word), O(n * L) space for the groups.
# The dict keeps keys in insertion order, which gives the required group
# order for free.
# Alternative: use a tuple of 26 letter counts as the key instead of the
# sorted word. That is O(n * L) time and worth it only for very long words.
