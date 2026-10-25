"""Lab 5 (chapter 5): build a byte-pair-encoding tokenizer from scratch. Pure Python, no libraries.

Run:  python lab05-bpe.py
Then edit TEXT or NUM_MERGES and run again.
"""
from collections import Counter

TEXT = "low lower lowest newer newest wider widest low low newer newer"
NUM_MERGES = 10

# Start with the text as a list of single characters (a space is a character too).
tokens = list(TEXT)
print("start:", len(tokens), "tokens")

merges = []  # the learned rules, in order: (left, right) -> joined
for i in range(NUM_MERGES):
    pairs = Counter(zip(tokens, tokens[1:]))
    if not pairs:
        break
    (left, right), count = pairs.most_common(1)[0]  # the most frequent adjacent pair
    if count < 2:
        break  # nothing repeats any more, so merging would not shorten the text
    merges.append((left, right))
    merged, out, j = left + right, [], 0
    while j < len(tokens):
        if j + 1 < len(tokens) and tokens[j] == left and tokens[j + 1] == right:
            out.append(merged)
            j += 2
        else:
            out.append(tokens[j])
            j += 1
    tokens = out
    print(f"merge {i + 1:2d}: {left!r} + {right!r} -> {merged!r}   ({count}x)  now {len(tokens)} tokens")

print("\nvocabulary:", sorted(set(tokens)))


def encode(text: str) -> list[str]:
    """Apply the learned merges, in the order they were learned, to new text."""
    toks = list(text)
    for left, right in merges:
        out, j = [], 0
        while j < len(toks):
            if j + 1 < len(toks) and toks[j] == left and toks[j + 1] == right:
                out.append(left + right)
                j += 2
            else:
                out.append(toks[j])
                j += 1
        toks = out
    return toks


print("\nencode('lowest newest'):", encode("lowest newest"))
print("encode('slowly'):       ", encode("slowly"), " <- an unseen word falls back to smaller pieces")
