---
id: l31
title: "Self-attention: queries, keys and values"
quiz: quiz-03.yaml
resources: []
sources: [20, 1]
---
After this lesson you can walk through self-attention for a short sentence in six steps, and say what queries, keys and values are for.

## Attention within one sentence

In the 2014 design (lesson 30), the decoder attended over the encoder's vectors. **Self-attention** applies the idea inside a single sequence: every token looks at the other tokens of the same sentence and blends in the ones most relevant to it. The Transformer introduced in 2017 is built on attention alone, "dispensing with recurrence and convolutions entirely". [1]

For "the cat sat on it", the vector for "it" should pull in information from "cat". Self-attention is how that happens.

## Six steps

The steps below follow Jay Alammar's The Illustrated Transformer. [20]

1. **Create a query, a key and a value for every token.** Multiply each token's embedding by three learned weight matrices. Think of the *query* as "what am I looking for?", the *key* as "what do I contain?", and the *value* as "what do I pass along if you attend to me?". The article itself calls these abstractions that help in thinking about attention. [20]
2. **Score.** For one token, take the dot product of its query with the key of every token in the sentence, itself included. A higher score means more relevant. [20]
3. **Scale.** Divide each score by the square root of the key size (8 when keys have 64 numbers). The Transformer paper explains why: if the components of a query and a key are independent with mean 0 and variance 1, their dot product has mean 0 and variance d_k, so for large d_k the dot products grow large and push softmax into regions where its gradients are extremely small. Dividing by √d_k counteracts that. [1][20]
4. **Softmax.** Turn the scores into positive weights that add up to 1. [20]
5. **Weight the values.** Multiply each token's value vector by its weight. Relevant tokens keep their influence; irrelevant ones fade towards zero. [20]
6. **Sum.** Adding the weighted value vectors gives this token's output, which goes on to the next layer. [20]

In matrix form all tokens are processed at once, which is what makes Transformers fast to train: no waiting for the previous token (the weakness of RNNs, lesson 12). The paper writes the whole thing as `Attention(Q, K, V) = softmax(QKᵀ / √d_k) V`. [1][20]

## Why self-attention beat recurrence on paper

The Transformer paper compares three kinds of layer on three properties, with n the sequence length and d the vector size. [1]

| Layer type | Work per layer | Sequential steps | Longest path between two tokens |
| --- | --- | --- | --- |
| Self-attention | O(n² · d) | O(1) | O(1) |
| Recurrent | O(n · d²) | O(n) | O(n) |
| Convolutional | O(k · n · d²) | O(1) | O(log_k n) |

Read the table like this. Self-attention needs only a constant number of sequential steps and any two tokens are one step apart, which makes long-range dependencies easier to learn than in a recurrent network where a signal must pass through up to n steps. The price is the n² term: work and memory grow with the square of the length, which is why long contexts are expensive (lesson 64). [1] The paper notes that self-attention is cheaper than recurrence when n is smaller than d. [1]

## A picture of the result

The lab prints a small table of attention weights for "the cat sat": row = the token that is looking, column = the token it looks at. Each row adds up to 1. With random stand-in weights the pattern is arbitrary; in a trained model the weights carry linguistic meaning, as in the "it" and "cat" example above.

:::key-takeaways
- Self-attention lets each token mix in information from other tokens of the same sequence. [20]
- Each token produces a query, a key and a value; scores are query·key, scaled, passed through softmax, and used to weight the values. [20]
- All tokens are computed at once in matrices, so training parallelises. [1]
:::

:::glossary
- **Self-attention**: attention where a sequence attends to itself.
- **Query / key / value**: three vectors per token: what it looks for / what it offers for matching / what it passes on.
- **Dot product**: multiply two vectors element by element and add up; large when they point the same way.
- **Weight matrix**: a learned grid of numbers that transforms vectors.
- **Scaling**: dividing scores by a constant (the square root of the key size) so they stay moderate.
- **Softmax**: turns scores into weights that sum to 1.
- **Parallel**: doing many computations at the same time.
:::
