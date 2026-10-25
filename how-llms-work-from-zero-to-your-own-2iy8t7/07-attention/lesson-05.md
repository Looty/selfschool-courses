---
id: l33
title: Many heads, and many layers
quiz: quiz-05.yaml
resources: []
sources: [1]
---
After this lesson you can explain multi-head attention and why models stack many layers.

## Why one attention is not enough

A single attention step produces one set of weights per token: one pattern of "who looks at whom". But a token may need several kinds of information at once: its subject, the previous word, a matching bracket. One weighted mix has to blend them all.

## Multi-head attention

The fix is to run several attentions in parallel, each with its **own** learned query, key and value matrices. Each is called a **head**. Every head produces its own output for the token; the outputs are concatenated and mixed by one more learned matrix. In the paper's words, instead of one attention over d_model-dimensional keys, values and queries, "we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections". The original used h = 8 heads, each with d_k = d_v = d_model / h = 64 (so d_model = 512), and because each head is smaller the total cost is similar to a single full-size head. [1] The paper's reason: multi-head attention lets the model attend "to information from different representation subspaces at different positions"; with a single head, averaging inhibits this. [1] It also tested the claim: keeping the amount of computation constant while varying the number of heads, single-head attention was 0.9 BLEU worse than the best setting, and quality also dropped off with too many heads. [1] The base model had about 65 million parameters (the "big" model, 213 million). [1]

(The mini-GPT you train in chapter 8 uses 4 heads with 64 numbers per token: each head works on 16 of them, so the cost stays about the same as one big attention.)

## Layers

A Transformer block, covered in the next chapter, contains attention followed by a small neural network, and a model stacks many such blocks: the original Transformer used N = 6 identical layers in each of its encoder and decoder stacks. [1] Later blocks work on the already-mixed output of earlier ones, so information can flow over several hops: the first layers may link neighbouring words, later ones larger structure. How each layer specialises is learned, and explaining exactly what each head does is an active research problem; it is not something these sources establish.

## What this chapter gave you

By now you have all the ingredients of attention: embeddings plus positions (lesson 23), queries, keys and values (lesson 31), a causal mask (lab 7), and heads. Chapter 8 assembles them into a GPT.

:::low-confidence
The claim that early layers link neighbouring words and later layers handle larger structure is a common intuition, not a finding established by the sources read for this course. The sources describe the mechanism of a single head, not what each head learns.
:::

:::key-takeaways
- Multi-head attention runs several attentions in parallel with separate learned matrices, then combines their outputs; the original used 8 heads of size 64. [1]
- Several heads give the layer different ways to look at the sentence.
- Models stack many blocks so later layers build on earlier mixing.
:::

:::glossary
- **Head**: one independent attention computation with its own query, key and value matrices.
- **Multi-head attention**: several heads run in parallel and their outputs combined.
- **Representation subspace**: a different "view" of the same vectors, produced by a different learned matrix.
- **Block / layer**: one repeated unit of the network.
- **Stack**: layers applied one after another.
- **Interpretability**: the research field of working out what a network's parts do.
:::
