---
id: l23
title: "Embeddings: tokens become vectors"
quiz: quiz-04.yaml
resources: []
sources: [7, 15, 20, 1, 41, 61]
---
After this lesson you can explain what an embedding table is, why position also needs encoding, and what the model actually receives.

## From integer to vector

After tokenization the text is a list of integers, such as `[17, 905, 42, 311, 8]` (made-up ids for illustration). An integer alone is a poor input: token 905 is not "close to" token 906 in any meaningful way. So the first layer of an LLM is an **embedding table**: a big grid with one row per token in the vocabulary. To embed a token you look up its row, a vector of numbers (lesson 14). [7][20]

Two details matter.

- The rows start random and are **learned by training**, like every other weight. Tokens used in similar contexts end up with similar vectors, the effect Bengio's paper and word2vec showed. [15][7]
- The size of the vector is a design choice. The mini-GPT you will train uses 64 numbers per token; real models use hundreds or thousands.

## Order must be added back

A sentence is not a bag of words: "dog bites man" differs from "man bites dog". Attention (chapter 7) looks at all tokens at once and does not by itself know their order. So models add information about **position**. The simplest version, used in the mini-GPT, is a second learned table with one row per position (1st, 2nd, 3rd, ...), and the input to the model is the token's vector plus its position's vector.

## How the original Transformer encoded position

The Transformer paper states the problem exactly: since the model contains no recurrence and no convolution, "in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens". It adds **positional encodings** to the input embeddings, with the same dimension d_model so the two can be summed. [1]

Instead of a learned table it used fixed sine and cosine waves of different frequencies:

```
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

where `pos` is the token's position and `i` the dimension. Each dimension is a sinusoid, with wavelengths forming a geometric progression from 2π to 10000 · 2π. The authors chose it because they hypothesised that it lets the model easily learn to attend by relative position (for any fixed offset k, the encoding at pos+k is a linear function of the encoding at pos) and because it may let the model extrapolate to longer sequences than those seen in training. They also tried learned position embeddings and found the two versions produced nearly identical results. [1]

Later models changed this again. GPT-1 used learned position embeddings "instead of the sinusoidal version proposed in the original work". [41] Rotary position embedding (RoPE, 2021) encodes absolute position with a rotation matrix and builds relative-position dependence directly into self-attention; its authors report it handles flexible sequence lengths and that the dependency between tokens decays as their distance grows. [61] The lab's mini-GPT uses the GPT-1 style, a learned table.

## What the model receives

For each token position, one vector: token embedding plus position embedding. A 64-token context with 64 numbers per token is a grid of 64 × 64 numbers. Everything that happens in the next chapters is arithmetic on grids like this one, and at the end the model produces a score for each token in the vocabulary, turned into probabilities to pick the next token (lesson 25).

:::key-takeaways
- An embedding table has one learned vector per token; looking up the row embeds the token. [7][20]
- Similar tokens end up with similar vectors because of how they are used in training. [15]
- Position is added separately so word order is not lost.
:::

:::glossary
- **Embedding table**: a grid with one learned row (vector) for each token in the vocabulary.
- **Lookup**: fetching a row by its token id.
- **Embedding dimension**: how many numbers per vector.
- **Positional encoding / position embedding**: extra information telling the model where each token sits in the sequence.
- **Bag of words**: treating text as a set of words with the order thrown away.
- **Learned**: found by training, not designed by hand.
:::
