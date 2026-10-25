---
id: l18
title: Neurons and layers
quiz: quiz-04.yaml
resources: []
sources: [33]
---
After this lesson you can describe a neuron and a layer, count parameters, and explain why a network needs a non-linear step between layers.

## One neuron

A **neuron** (or node) takes the values coming in, multiplies each by its own weight, adds them up, and adds a bias. In the Google crash course, a hidden-layer neuron's value comes from "a weighted sum of the previous layer's values plus a bias". [33] That is the straight-line model from lesson 15, with several inputs instead of one.

## Layers

Neurons are arranged in **layers**. Input nodes just hold the input values, and the output node gives the prediction. The layers in between are **hidden layers**: they let the model recombine the input using another set of parameters, and then recombine the result again. [33]

The crash course's example network has 3 inputs, a hidden layer of 4 neurons and 1 output, and it counts 21 parameters (weights and biases). [33] You can check: the hidden layer has 3 × 4 = 12 weights plus 4 biases, the output has 4 weights plus 1 bias, and 12 + 4 + 4 + 1 = 21. Counting parameters is how model sizes like "175 billion" are stated. [33]

## Why a plain stack does not work

If every neuron only computed a weighted sum, stacking layers would add nothing: "linear calculations performed on the output of linear calculations are also linear", so the whole network collapses to one straight-line model that cannot learn nonlinear patterns. [33] This is the same limit that stopped the single-layer perceptron on XOR (lesson 10).

The fix is an **activation function**: a simple non-linear step applied to each neuron's output, such as setting negative values to zero. It is what lets deeper networks learn curved, complicated patterns. [33]

:::low-confidence
The crash-course page defers activation functions to a later page, which was not read. The ReLU example ("set negatives to zero") is a standard illustration, not a quotation from the source. [33]
:::

## What a language model adds

An LLM's layers are not plain layers like these; they use attention (chapters 7 and 8). But they are still built from the same pieces: weighted sums, non-linear steps, stacked in layers, with all the weights found by gradient descent.

:::key-takeaways
- A neuron computes a weighted sum of its inputs plus a bias. [33]
- Hidden layers sit between input and output; the 3-4-1 example has 21 parameters. [33]
- Without a non-linear activation, stacked layers collapse into a linear model. [33]
:::

:::glossary
- **Neuron (node)**: a unit that computes a weighted sum of its inputs plus a bias.
- **Layer**: a group of neurons that work side by side.
- **Hidden layer**: a layer between the input and the output.
- **Parameter count**: the total number of weights and biases; a measure of model size.
- **Linear**: made only of multiplying by constants and adding; a straight-line relationship.
- **Non-linear**: not a straight line; able to curve.
- **Activation function**: a non-linear step applied to a neuron's output.
- **Network (neural network)**: layers of neurons connected by weights.
:::
