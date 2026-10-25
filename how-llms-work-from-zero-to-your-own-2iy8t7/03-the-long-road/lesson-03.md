---
id: l13
title: "A neural language model (Bengio, 2003)"
quiz: quiz-03.yaml
resources: []
sources: [15]
---
After this lesson you can explain the curse of dimensionality for language, and how learned word vectors let a model generalise to sentences it has never seen.

## The count-everything wall

Shannon's counting approach (lesson 7) and its descendants, n-gram models, estimate the probability of a word from counts of the words before it. The wall they hit is not the computer; it is the data. Almost every long sequence of words you will ever read is a sequence nobody has written before. A table of counts has nothing to say about it.

Bengio and colleagues state this directly: learning the joint probability of word sequences is "intrinsically difficult because of the curse of dimensionality". A test sequence will usually differ from every sequence in the training data, so a model must **generalise** to unfamiliar combinations of words. [15]

## Their idea

The 2003 paper "A Neural Probabilistic Language Model" proposes two things learned together. [15]

1. A **distributed representation** for each word: a list of numbers, the word's *vector*, instead of treating each word as an unrelated symbol.
2. A **neural network** that takes the vectors of the previous words and computes the probability of the next word.

The payoff is the generalisation. If "dog" and "cat" end up with similar vectors, then having seen "the cat is walking in the bedroom" helps the model assign sensible probability to "a dog was running in a room", a sentence it never saw. Words with similar representations let the model give reasonable probability to new sequences built from familiar-like words. [15]

The authors report that this approach beat state-of-the-art n-gram models on two text collections and could use longer contexts. [15] The baseline they beat was a strong one: modified Kneser-Ney smoothed n-grams, which they note worked significantly better than standard back-off models. [15]

The paper is also frank about cost. The larger of its two experiments, on AP News, ran for only 5 epochs but took over 3 weeks on 40 CPUs. [15] Compare that with the mini-GPT you will train in a minute on one laptop: hardware and algorithms have changed enormously since 2003, and "feasible to train" is one of the main things that moves in this history.

## Why this paper is a hinge

Everything in modern language models shows up here in small form: words (later tokens) become vectors, a neural network turns a context into a probability for the next word, and the vectors are learned as a by-product of getting the predictions right. The remaining chapters swap better parts into this same frame.

:::key-takeaways
- Sequences of words are almost always new, so a model must generalise beyond counts: the curse of dimensionality. [15]
- Bengio et al. (2003) learned word vectors and a neural network together to predict the next word. [15]
- Similar words get similar vectors, which lets knowledge transfer to unseen sentences. [15]
:::

:::glossary
- **Curse of dimensionality**: the number of possible inputs grows so fast that training data covers almost none of them.
- **Generalise**: perform well on new inputs, not just the training ones.
- **n-gram model**: a language model built from counts of n-word sequences.
- **Distributed representation**: describing each item by a vector of numbers rather than a single symbol.
- **Word vector**: the list of numbers that represents one word.
- **Joint probability**: the probability of a whole sequence of words.
- **Corpus (plural corpora)**: a collection of text used for training or testing.
:::
