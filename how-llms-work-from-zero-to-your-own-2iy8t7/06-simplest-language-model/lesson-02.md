---
id: l25
title: Sampling and temperature
quiz: quiz-02.yaml
resources: []
sources: [30, 58, 70]
---
After this lesson you can explain greedy versus sampled generation, and how temperature reshapes the probabilities before a choice is made.

## A model gives probabilities, you pick

A language model's output for each step is a probability for **every** token in its vocabulary. Turning that into one actual token is a separate decision, called **decoding**. The Hugging Face documentation describes two basic strategies. [30]

- **Greedy search** picks the most likely token every time. The documentation notes it works well for input-grounded tasks such as transcription and translation, but is not optimal for creative uses such as story writing or chat. [30] You saw it loop in lab 1.
- **Sampling** picks at random, in proportion to the probabilities. A token with probability 0.4 is picked 40% of the time. Output varies from run to run. [30]

## Temperature

Temperature is a dial on how adventurous sampling is. The documentation's description: it controls how unpredictable the next selected token will be, with high values (above about 0.8) good for creative tasks and low values (below about 0.4) for tasks that need careful "thinking"; it only applies when sampling is on. [30]

How it works, for the simple version in the lab: each probability is raised to the power 1/T and the results are renormalised so they add up to 1.

- **T below 1 sharpens** the distribution: the likely tokens get even likelier. At T → 0 you get greedy decoding.
- **T = 1** leaves the model's probabilities alone.
- **T above 1 flattens** it: unlikely tokens get a real chance, and at very high T the choice approaches uniform random.

(Real models apply the temperature to the raw scores before they become probabilities, which gives the same effect; the lab's shortcut is equivalent for the point being made.)

## Why greedy and low temperature loop

Karpathy's well-known 2015 post on character-level models shows this directly: sampling at a temperature near zero makes the model fall into repetitive loops, while lower values generally give more conservative output. [70] The "Neural Text Degeneration" paper makes the same point about word-level models: using likelihood as a decoding objective "leads to text that is bland and strangely repetitive", and decoding choice alone can greatly change quality even with the same model. [58]

Their remedy is **nucleus sampling** (also called top-p): at each step, keep only the smallest set of most likely tokens whose probabilities add up to p (say 0.9), renormalise, and sample from that "nucleus". It keeps diversity while cutting off the unreliable long tail of very unlikely tokens, and the authors report text closer to human quality. [58] In the Hugging Face library it is one more option of `generate()`. [30]

## Why it matters

No setting is correct for everything. For answering a factual question you want low temperature or greedy. For brainstorming you want higher. And because the model's mistakes compound (one odd token changes everything after it), high temperature makes long outputs drift.

:::key-takeaways
- Decoding turns a model's probabilities into a chosen token: greedy takes the most likely; sampling draws at random. [30]
- Temperature sharpens (low) or flattens (high) the distribution before sampling. [30]
- Low temperature suits careful tasks; high suits creative ones. [30]
:::

:::glossary
- **Decoding**: the rule for choosing one token from the model's probabilities.
- **Greedy search**: always take the single most likely token.
- **Sampling**: draw the next token at random, weighted by probability.
- **Temperature**: a setting that sharpens (low) or flattens (high) the distribution before sampling.
- **Distribution**: the full list of probabilities, one per token.
- **Normalise**: rescale numbers so they add up to 1.
- **Beam search**: a decoding method that keeps several candidate continuations at once (mentioned in the documentation).
:::
