"""Lab 7 (chapter 7): self-attention for one tiny sentence, step by step, with numpy.

Setup:  uv venv && uv pip install numpy
Run:    python lab07-attention.py
"""
import numpy as np

rng = np.random.default_rng(1)
words = ["the", "cat", "sat"]
d = 4  # size of each word's vector (real models use hundreds or thousands)

# Each word starts as a vector of numbers (an embedding). Here they are random stand-ins.
X = rng.normal(size=(len(words), d))

# Three learned matrices turn each word into a query, a key and a value. Here they are random stand-ins.
Wq, Wk, Wv = (rng.normal(size=(d, d)) for _ in range(3))
Q, K, V = X @ Wq, X @ Wk, X @ Wv

# Step 1: score every word against every other: the dot product of a query with each key.
scores = Q @ K.T / np.sqrt(d)  # dividing by sqrt(d) keeps the numbers from getting too large

# Step 2 (for a GPT): a word may only look at itself and earlier words, never ahead.
mask = np.triu(np.ones_like(scores), k=1).astype(bool)
scores = np.where(mask, -np.inf, scores)


# Step 3: softmax turns each row of scores into weights that are positive and add up to 1.
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


weights = softmax(scores)

# Step 4: each word's new vector is the weighted mix of the value vectors.
out = weights @ V

print("attention weights (row = the word that is looking, column = the word it looks at):")
print("          " + "  ".join(f"{w:>6}" for w in words))
for w, row in zip(words, weights):
    print(f"{w:>8}  " + "  ".join(f"{x:6.2f}" for x in row))
print("\nrows add up to 1:", weights.sum(axis=1).round(3))
print("output shape:", out.shape, "(one new vector per word, same size as before)")
