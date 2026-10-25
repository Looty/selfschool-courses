---
id: l62
title: "Optimisers: from gradient descent to Adam"
quiz: quiz-06.yaml
resources: []
sources: [46, 1, 41, 32]
---
After this lesson you can explain what an optimiser adds to plain gradient descent, and what warmup and a learning-rate schedule are.

## Plain gradient descent, with a catch

Lesson 16's update was `new weight = old weight − step size × slope`, repeated until the model converges. [32] For a model trained on millions of examples, computing the slope on all of them for every step is slow, so in practice each step uses a small random group, a **minibatch**: "stochastic" gradient descent. The slope from a minibatch is a noisy estimate of the true one.

Two problems follow. The noise makes progress jagged, and one learning rate for every parameter is a crude choice: some weights need big steps, others tiny ones.

## Adam

Adam (Kingma and Ba, December 2014, ICLR 2015) is the optimiser used almost everywhere in this course's papers. It is described as a first-order, gradient-based method built on "adaptive estimates of lower-order moments" of the gradients. In plain words, for each parameter it keeps running averages of recent gradients (their direction) and of their squared size (their scale), and takes steps that depend on both: bigger where the gradient has been consistent and small, smaller where it is large or noisy. The authors list its attractions: straightforward to implement, computationally efficient, little memory, invariant to diagonal rescaling of the gradients, suited to problems with large data or many parameters, suited to noisy or sparse gradients, and hyperparameters with intuitive meanings that usually need little tuning. [46] The mini-GPT labs use AdamW, a variant with weight decay.

## Learning rate is not constant

Even with Adam, the learning rate is a schedule over training. The Transformer paper used Adam with β1 = 0.9, β2 = 0.98 and ε = 10⁻⁹ and varied the learning rate: increasing it **linearly for the first 4000 steps (warmup)**, then decreasing it proportionally to the inverse square root of the step number. [1] GPT-1 did something similar: a maximum learning rate of 2.5e-4, increased linearly from zero over the first 2000 updates and then annealed to 0 with a cosine schedule. [41]

Why warm up? Early in training the weights are random and the gradient estimates unreliable, so large steps can do damage; a gentle start, then a decay as the model approaches a good region, is the usual shape. (This explanation is the common one; the papers state the schedules, not the reasons.)

## Regularisation in one line

The Transformer paper also used dropout of 0.1 on each sub-layer output and on the sums of embeddings and positions, and label smoothing of 0.1, which "hurts perplexity, as the model learns to be more unsure, but improves accuracy and BLEU". [1] These are ways to reduce overfitting (lesson 19).

## What to remember

When a training run misbehaves, the usual suspects are in this lesson: a learning rate that is too high or low (lab 4), no warmup, or too little data for the model (lesson 40). In the mini-GPT labs the learning rate is fixed (3e-3 or 2e-3) and AdamW does the rest.

:::key-takeaways
- Training uses minibatches, so each gradient is a noisy estimate. 
- Adam keeps running averages of each parameter's gradient and squared gradient to scale its step. [46]
- Learning rate follows a schedule: warmup (4000 steps in the Transformer paper), then decay. [1][41]
:::

:::glossary
- **Minibatch / stochastic gradient descent (SGD)**: updating from a small random group of examples at a time.
- **Optimiser**: the rule that turns gradients into weight updates (SGD, Adam, AdamW).
- **Adam**: an optimiser that adapts each parameter's step using running averages of its gradient and squared gradient.
- **Moment**: here, a running average of the gradient (first) or its square (second).
- **Warmup**: starting with a small learning rate and increasing it over the first steps.
- **Learning-rate schedule**: how the learning rate changes during training (for example warmup then decay).
- **Cosine schedule**: a smooth decay following part of a cosine curve.
- **Dropout**: randomly switching off part of the network during training to reduce overfitting.
- **Label smoothing**: making the training target slightly less than 100% certain.
- **AdamW**: Adam with weight decay applied separately.
:::
