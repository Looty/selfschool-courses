"""Reference solution for word_count_top (see word_count_top_starter.py)."""
from collections import Counter


def word_count_top(text: str, k: int) -> list[str]:
    """Return the k most frequent words, ties broken alphabetically."""
    counts = Counter(text.lower().split())
    ranked = sorted(counts, key=lambda word: (-counts[word], word))
    return ranked[:k]

# Complexity: O(n) to split and count n characters, then O(m log m) to sort
# the m distinct words. Space O(m) for the counter plus O(n) for the split.
# The key (-count, word) sorts by count descending and by word ascending in
# one pass; reverse=True would flip the alphabetical order as well.
# Trap: Counter.most_common(k) keeps equal counts in first-seen order, so it
# fails example 2 of the statement.
# Alternative when k is much smaller than m:
#     heapq.nsmallest(k, counts, key=lambda word: (-counts[word], word))
# which keeps only k candidates in memory at a time.
