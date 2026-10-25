---
id: l24
title: Predicting the next character by counting
quiz: quiz-01.yaml
resources: []
sources: [34, 31, 17]
---
After this lesson you can build the simplest language model there is, a table of counts, and explain how it turns counts into probabilities.

## The simplest model

Pick a piece of text. Look at every pair of neighbouring characters, such as `t` followed by `h`. Count how often each character follows each other character. That table of counts **is** the model. It is a **bigram** model: "an N-gram in which N=2", a pair of consecutive units. [34] It is Shannon's third rung (lesson 7), applied to characters. [31]

The data for the lab is the 1 MB of Shakespeare used in the nanoGPT README. [17] In the test run it contained 65 distinct characters, and after a `t` the most common next characters were `h` (20,592 times), a space (14,879), `o` (5,328), `e` (3,918) and `i` (2,698).

## From counts to probabilities

Counts become probabilities by dividing by the total. If a `t` was followed by something 60,000 times in all, and by `h` 20,592 of those, then P(next is `h` | previous is `t`) is about 0.34.

One practical fix: a pair that never appeared would get probability exactly zero, and one zero would make any text containing it impossible. The usual cure is **smoothing**: add 1 to every count before dividing, so nothing has probability zero. The lab does this.

## Generating text

To write text, start with any character and repeat: look up the probabilities for the character that follows the current one, pick the next character at random in proportion to them, and move on. That is the same loop as in lesson 2, with the simplest possible model inside it.

The result reads like this (from the lab):

```
The merParthathavout:
Whe irtthogor s.
P lof. blayon fes mororveine:
```

It has the look of English words and line breaks and none of the meaning. It cannot do better, because it sees only **one** character of context. The word "Whe" is plausible letter by letter and nothing links it to the next word.

## Why this matters

Everything after this chapter is about giving the model more context and a better way to use it, while keeping the same job: assign a probability to every possible next token. The bigram is the baseline to beat. Any model that cannot beat it has learned nothing.

:::key-takeaways
- A bigram model is a table of counts of what follows each character; counts divided by totals give probabilities. [34]
- Smoothing (add 1 to every count) prevents zero probabilities.
- With one character of context the output looks like English but means nothing.
:::

:::glossary
- **Bigram**: a pair of consecutive items; here, two characters in a row. [34]
- **Count table**: the grid recording how often each character follows each other one.
- **Conditional probability**: the probability of one thing given another, such as the next character given the previous one.
- **Smoothing**: adding a small amount to every count so unseen pairs do not get probability zero.
- **Baseline**: a simple model that any better model must beat.
- **Context (here)**: the earlier characters the prediction uses; a bigram uses one.
:::
