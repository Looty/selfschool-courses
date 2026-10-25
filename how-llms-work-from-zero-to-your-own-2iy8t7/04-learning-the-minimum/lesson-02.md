---
id: l16
title: Gradient descent
quiz: quiz-02.yaml
resources: []
sources: [32]
---
After this lesson you can describe gradient descent in four steps, and say what the learning rate does and what goes wrong when it is too big.

## Walking downhill in fog

Imagine the loss as a landscape. Each point is one choice of knob settings, and its height is the loss there. You want the lowest point, but you can only feel the slope under your feet. **Gradient descent** is the strategy: feel the slope, take a small step downhill, repeat. [32]

For a straight-line model with MSE loss, plotting loss against the weight and bias forms a surface. For linear models that surface is convex (a single bowl), so gradient descent can reach the minimum. [32]

## The four steps

The Google crash course lists them. [32]

1. Calculate the loss with the current weight and bias.
2. Work out the direction that reduces loss.
3. Move the weight and bias a small amount in that direction.
4. Repeat until the loss stops going down.

The slope for each parameter is the **gradient**, the derivative of the loss with respect to that parameter. For MSE on a line it is, for the weight, the average of (prediction − truth) × 2x, and for the bias the average of (prediction − truth) × 2. [32] Moving against the slope lowers the loss:

```
new weight = old weight − step size × weight slope
new bias   = old bias   − step size × bias slope
```

The step size is usually called the **learning rate**. The crash-course page calls it a "small amount" and uses 0.01 as an arbitrary example. [32]

## Convergence

When further steps no longer reduce the loss, the model has **converged**. The loss may keep wobbling slightly around its lowest values, so training should run until the loss stabilises. [32]

## The learning rate is a real choice

- **Too small:** progress is slow. You may stop before converging.
- **Too big:** each step overshoots the bottom and lands higher up the other side. The loss can bounce or even grow without limit.

You will see both in the next lab. A large language model is trained with the same four steps; backpropagation (lesson 11) is how the slopes for billions of weights are computed efficiently.

:::key-takeaways
- Gradient descent: compute loss, find the downhill direction, step a small amount, repeat. [32]
- The gradient is the slope of the loss with respect to each parameter; the update is old value minus step size times slope. [32]
- Too small a learning rate is slow; too big can make the loss grow.
:::

:::glossary
- **Gradient descent**: repeatedly stepping the parameters in the direction that lowers the loss.
- **Gradient**: the slope of the loss with respect to each parameter.
- **Learning rate**: how big each step is.
- **Convex**: shaped like a single bowl, with one lowest point.
- **Converge**: reach a point where more steps no longer lower the loss.
- **Overshoot**: stepping so far that you pass the lowest point.
- **Iteration / step**: one pass of computing the loss and updating the parameters.
:::
