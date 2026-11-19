"""Top k words (function style: return a value, do not print).

Given a text and a number k, return the k most frequent words.

Input
    text: a string of words separated by whitespace (spaces, tabs, newlines).
          Words contain only letters and digits. Compare words without
          regard to case: "Disk" and "disk" are the same word.
    k:    how many words to return (k >= 0).

Output
    A list of lower-case words, most frequent first. Words with the same
    count are ordered alphabetically. If the text has fewer than k distinct
    words, return all of them.

Constraints
    len(text) <= 10**6

Example 1
    word_count_top("disk cpu disk net cpu disk", 2)  ->  ["disk", "cpu"]

Example 2 (tie: "cpu" and "net" both appear once, alphabetical order wins)
    word_count_top("net cpu disk disk", 2)  ->  ["disk", "cpu"]

Example 3 (edge cases)
    word_count_top("", 3)          ->  []
    word_count_top("Disk DISK", 5) ->  ["disk"]

In a function-style question the grader looks at the return value only.
Anything you print goes to a separate debug panel.
"""


def word_count_top(text: str, k: int) -> list[str]:
    """Return the k most frequent words, ties broken alphabetically."""
    raise NotImplementedError
