---
id: l15
title: Learning from examples, and measuring error
quiz: quiz-01.yaml
resources: []
sources: [32, 34]
---
After this lesson you can describe a model as a function with adjustable numbers, and explain why training needs a single number called loss.

## A model is a function with knobs

Start with the simplest model there is: a straight line, `prediction = w × x + b`. The numbers `w` (the weight) and `b` (the bias) are the knobs. Give it a house size `x` and it predicts a price. With `w = 0` and `b = 0` every prediction is 0, which is wrong; with the right knobs the line passes close to the real prices. A model, at any size, is this: a function with adjustable numbers. A large language model is the same idea with billions of knobs and a far more elaborate function.

**Training** means finding good settings for the knobs from examples. To do that the computer needs a way to tell better settings from worse ones.

## Loss: one number for "how wrong"

A **loss** is a single number that says how far the model's predictions are from the right answers; training tries to make it small. For predicting numbers, a standard loss is the **mean squared error (MSE)**: for each example take the difference between prediction and truth, square it, and average over the examples. [32] Squaring makes every error positive and punishes big misses harder.

For predicting *which category* (and language modelling is exactly that: which token comes next, out of tens of thousands), the standard loss is **cross-entropy**, which the Google glossary describes as a generalization of log loss to multi-class classification and which quantifies the difference between two probability distributions. [34] You do not need the formula yet. What matters: if the model gives the right next token a probability near 1, the loss is near 0; if it gives that token a tiny probability, the loss is large.

## Why a single number matters

Once "how wrong" is one number, learning becomes an ordinary search problem: change the knobs in whatever direction lowers the number. The next lesson gives the standard recipe.

:::key-takeaways
- A model is a function with adjustable numbers (weights and biases). [32]
- Loss is one number saying how wrong the predictions are; for numbers a common loss is mean squared error. [32]
- For picking among categories, such as the next token, the standard loss is cross-entropy. [34]
:::

:::glossary
- **Weight / bias**: the adjustable numbers in a model: a multiplier on an input, and a constant added.
- **Prediction**: the model's output for an input.
- **Loss**: a number measuring how far predictions are from the right answers; lower is better.
- **MSE (mean squared error)**: the average of the squared differences between predictions and truth.
- **Cross-entropy**: a loss for predicting categories; small when the right category gets high probability.
- **Probability distribution**: a list of probabilities, one per option, that add up to 1.
- **Multi-class classification**: choosing one of many categories, as when choosing the next token.
:::
