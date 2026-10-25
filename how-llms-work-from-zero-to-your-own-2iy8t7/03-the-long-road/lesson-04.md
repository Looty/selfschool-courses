---
id: l14
title: "Word vectors at scale (word2vec, 2013)"
quiz: quiz-04.yaml
resources: []
sources: [7, 47]
---
After this lesson you can say what a word vector is, what word2vec added, and why cheap training mattered.

## Vectors as meaning-by-company

Bengio's model (lesson 13) learned word vectors as a by-product, but training it was slow. A 2013 paper from Google, "Efficient Estimation of Word Representations in Vector Space" by Mikolov, Chen, Corrado and Dean, proposed two new, much cheaper architectures for computing continuous vector representations of words from very large datasets. [7]

The headline was cost. The authors report substantial accuracy gains at much lower computational cost, and that learning high-quality vectors from a 1.6-billion-word dataset takes less than a day. [7] Quality was judged on a word-similarity task, comparing against the previous best neural-network techniques, and the vectors reached state-of-the-art results on a test set measuring both syntactic and semantic similarity. [7]

## Follow-up: the 2013 NeurIPS paper

A second paper by Mikolov and colleagues, "Distributed Representations of Words and Phrases and their Compositionality" (October 2013), built on the skip-gram model, "an efficient method for learning high-quality distributed vector representations". It added three practical ideas: subsampling very frequent words (which speeds up training and makes the vectors more regular), negative sampling (a simpler alternative to hierarchical softmax), and a method for finding phrases, because word vectors ignore word order and cannot represent idioms such as "Air Canada" from "Canada" and "Air". [47]

## What a vector means

A word vector is a list of, say, 300 numbers. The numbers are not designed by anyone. They are adjusted during training so that words used in similar contexts end up with similar vectors; "Paris" lands near "Rome" and far from "carrot". You can then measure how close two words are by how close their vectors are.

This is the idea that a word is known by the company it keeps, turned into arithmetic. It is also the first place most people meet *embeddings*: a table that maps each token to a vector. Every LLM begins with one (lesson 23).

## What it changed

Before 2013, representing a word often meant a one-hot vector: a long list of zeros with a single 1 saying which word it is, which makes every pair of words equally unrelated. Learned vectors gave models a notion of similarity for free, and reusing vectors trained on one big corpus in many tasks became standard practice. The next step, in 2017, was to make the representation of a word depend on the whole sentence around it; that is what the Transformer does.

:::key-takeaways
- word2vec (2013) trained good word vectors cheaply: under a day on 1.6 billion words. [7]
- Vectors are learned so that words used in similar contexts get similar vectors.
- An embedding is a table mapping each token to such a vector; LLMs start with one.
:::

:::glossary
- **word2vec**: Google's 2013 method for learning word vectors cheaply from large text.
- **Word vector / embedding**: the list of numbers that represents a word or token.
- **One-hot vector**: a list of zeros with a single 1 identifying a word; it carries no notion of similarity.
- **Similarity task**: a test that checks whether similar words get similar vectors.
- **Syntactic vs semantic**: about grammar (plural, tense) vs about meaning.
- **Continuous representation**: described by real-valued numbers rather than discrete symbols.
:::
