---
id: l28
title: The same model as a neural network
quiz: quiz-05.yaml
resources: []
sources: [20, 32, 33, 34]
---
After this lesson you can describe how a table of counts becomes a trained network, and what softmax and logits are.

## Replace the table with learnable numbers

The counting model stores one row of counts per character. Imagine instead a grid of **learnable numbers** with the same shape: one row per character, one column per possible next character. These numbers are not counts; they are called **logits**, raw scores where higher means "more likely next". This grid is exactly the embedding table of lesson 23, with one row per token and, here, as many columns as there are tokens. [33]

To predict, look up the row for the current character. It holds a score for every possible next character, but scores can be negative or huge, and probabilities must be positive and add up to 1.

## Softmax

The conversion is called **softmax**. In The Illustrated Transformer's description, softmax turns the scores into positive weights that sum to 1. [20] The recipe is: take e to the power of each score (making everything positive), then divide each by the sum of all of them (making them add to 1). A high score gets a high probability, and all probabilities add to 1. Dividing the scores by a temperature before softmax is exactly the temperature of lesson 25.

## Train it

Now we have the whole learning setup.

1. Look up the row for the current character, apply softmax, and read the probability given to the true next character.
2. Compute the loss: cross-entropy, minus the log of that probability. [34]
3. Compute the gradient of the loss with respect to every number in the grid (backpropagation, lesson 11).
4. Move every number a small step against its gradient (gradient descent, lesson 16). [32]
5. Repeat on many pairs of characters.

After enough steps, the learned scores line up with the log counts, so the network predicts almost exactly what the count table does. (This equivalence is standard teaching and was not checked in the sources read.)

## Why bother?

If it learns the same thing as counting, why change? Because the *counting* version cannot grow: more context means exponentially more rows (lesson 7). The *learned* version can replace the lookup with a deeper function of several previous characters, with a number of parameters that grows slowly. That is the move Bengio made (lesson 13), and the mini-GPT in chapter 8 is the same recipe with attention doing the work of the function.

:::low-confidence
That a trained one-layer network ends up matching the count table is a standard result in introductory courses, not something the sources read for this course state. It follows from minimising cross-entropy on the same pairs. [34]
:::

:::key-takeaways
- A bigram table can be replaced by a grid of learnable scores (logits), one row per current character. [33]
- Softmax turns scores into probabilities that are positive and sum to 1. [20]
- Training = cross-entropy loss + backpropagation + gradient descent. [32][34]
:::

:::glossary
- **Logits**: raw model scores before they are turned into probabilities.
- **Softmax**: converts scores into probabilities: exponentiate each, then divide by the total. [20]
- **Learnable grid**: a table of numbers adjusted by training.
- **Log count**: the logarithm of a count; the scores a trained bigram network tends to learn.
- **Equivalent**: gives the same predictions by a different route.
- **Scale (of parameters)**: how the number of parameters grows with the amount of context.
:::
