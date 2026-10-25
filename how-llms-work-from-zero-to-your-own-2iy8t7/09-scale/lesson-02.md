---
id: l39
title: Scaling laws
quiz: quiz-02.yaml
resources: []
sources: [2, 3]
---
After this lesson you can state what the scaling-law paper found, and why smooth trends made large investments rational.

## A surprise: it is predictable

In January 2020 Kaplan and colleagues at OpenAI published "Scaling Laws for Neural Language Models". Their central finding: cross-entropy loss (lesson 26) follows a **power law** with model size, dataset size and the compute used for training, and the trends hold across more than seven orders of magnitude, that is, a ten-million-fold range. [2]

A power law means plotting loss against size on log-log axes gives a straight line. In plain words: each time you multiply the model (or the data, or the compute) by a fixed factor, loss falls by a predictable factor. There are diminishing returns, but no sudden wall in the range they tested.

## What did not matter much

The same paper reports that architectural details such as the width or depth of the network have minimal effects within a wide range. [2] What mattered was the total scale. This is a big reason for the field's focus on making models bigger rather than redesigning them.

## What it allowed

Because the curves are smooth, you can train small models cheaply, fit the trend, and **predict** what a model ten or a hundred times bigger will achieve, before spending the money. The paper also provides simple equations for how overfitting depends on model and dataset size and how training speed depends on model size, and uses them to determine how to allocate a fixed compute budget. [2]

Its recommendation: larger models are notably more sample-efficient, so the most compute-efficient training uses very large models on a modest amount of data and stops well before convergence. [2] The next lesson shows that a later study reached a different conclusion about how to split the budget.

## From loss to abilities

Loss is a smooth number. The abilities people care about, such as answering questions from a few examples, appeared to improve with scale in the GPT-3 paper, which trained a model of 175 billion parameters and found few-shot performance improved substantially with size. [3] How loss translates into specific skills, and whether new abilities appear suddenly or gradually, is a matter of ongoing study that these sources do not settle.

:::key-takeaways
- Loss falls as a smooth power law in model size, data and compute, over more than seven orders of magnitude. [2]
- Network width and depth matter little within a wide range; total scale matters. [2]
- Smooth trends let you predict a big model's loss from small runs and plan a compute budget. [2]
:::

:::glossary
- **Scaling law**: a regular, predictable relationship between loss and scale (size, data, compute).
- **Power law**: a relationship where multiplying the input by a factor multiplies the output by another fixed factor.
- **Order of magnitude**: a factor of ten.
- **Compute**: the amount of computation used for training.
- **Sample-efficient**: needing fewer training examples to reach a given loss.
- **Compute budget**: the fixed amount of computation you can afford.
- **Log-log plot**: a chart with both axes on log scales, where power laws appear as straight lines.
:::
