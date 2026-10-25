"""Lab 6 (chapter 6): the simplest language model, built by counting. Pure Python.

Setup:  python lab-corpus.py        (creates input.txt)
Run:    python lab06-bigram.py
Then change TEMPERATURE below (0.5, 1.0, 2.0) and run again.
"""
import math
import random
from collections import Counter, defaultdict

TEMPERATURE = 1.0
random.seed(0)

text = open("input.txt", encoding="utf-8").read()
split = int(0.9 * len(text))
train, valid = text[:split], text[split:]

# 1. Count how often each character follows each character.
counts = defaultdict(Counter)
for a, b in zip(train, train[1:]):
    counts[a][b] += 1
vocab = sorted(set(text))
print(f"{len(vocab)} distinct characters; after 't' the most common next characters are:")
print("  ", counts["t"].most_common(5))


# 2. Turn counts into probabilities (add 1 to every count so nothing has probability zero).
def probs(prev: str) -> dict:
    c = counts[prev]
    total = sum(c.values()) + len(vocab)
    return {ch: (c[ch] + 1) / total for ch in vocab}


# 3. Generate: repeatedly pick the next character from the probabilities, with temperature.
def sample(prev: str) -> str:
    p = probs(prev)
    weights = [p[ch] ** (1.0 / TEMPERATURE) for ch in vocab]  # temperature < 1 sharpens, > 1 flattens
    return random.choices(vocab, weights)[0]


out, ch = [], "\n"
for _ in range(300):
    ch = sample(ch)
    out.append(ch)
print(f"\n--- 300 characters sampled at temperature {TEMPERATURE} ---")
print("".join(out))


# 4. Measure it: average negative log probability of the real next character on text it has not seen.
def avg_loss(s: str) -> float:
    return sum(-math.log(probs(a)[b]) for a, b in zip(s, s[1:])) / (len(s) - 1)


loss = avg_loss(valid[:20000])
print(f"\nvalidation loss: {loss:.3f} nats per character   (perplexity {math.exp(loss):.1f})")
print(f"guessing uniformly would score {math.log(len(vocab)):.3f}")
