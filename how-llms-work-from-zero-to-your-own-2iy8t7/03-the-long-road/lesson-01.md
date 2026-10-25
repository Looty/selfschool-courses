---
id: l11
title: Backpropagation and the second winter
quiz: quiz-01.yaml
resources: []
sources: [25, 26]
---
After this lesson you can say what backpropagation computes, why it made multilayer networks trainable, and what the second AI winter was.

## The training problem

Lesson 10 ended with a gap: a network with several layers can learn patterns a single layer cannot, but how do you adjust the weights in the *early* layers? You can see the final error, but each early weight affected it only indirectly, through everything after it.

## Backpropagation

**Backpropagation** efficiently computes the **gradient** of the loss with respect to a network's weights for one input-output example: how much the error would change if each weight moved a little. It works by passing derivatives backward, one layer at a time, from the output layer to the input layer, which avoids repeating calculations. Strictly the word names only this gradient step; people often use it loosely for the whole learning procedure, which also includes using the gradient to update the weights (gradient descent, next chapter). [25]

The ingredients are older than neural networks. The chain rule it relies on was written down by Leibniz in 1676. Frank Rosenblatt used the phrase "back-propagating error correction" in 1962 but did not know how to implement it for his networks, whose neurons gave discrete outputs with zero derivatives. Precursors also appeared in optimal control theory from the 1950s. [25]

:::low-confidence
The 1986 paper by Rumelhart, Hinton and Williams, usually credited with popularising backpropagation for neural networks, is the key event of this lesson, but the part of the reference article that covers it was not read, and the paper itself was not accessed. This lesson therefore states what backpropagation is and its earlier history, and does not describe the 1986 paper's contents. [25]
:::

## The second AI winter

Neural networks recovered in the 1980s, but a different part of AI collapsed. The second winter, roughly 1987 to 2000, had these causes according to the overview. [26]

- **The LISP machine market collapsed in 1987.** Cheaper workstations matched the specialised machines' speed, ending a market worth about half a billion dollars.
- **Expert systems proved brittle.** Programs such as XCON were costly to maintain, could not learn, and were useful only in narrow settings.
- **DARPA cut funding** for its Strategic Computing Initiative in 1987 and 1988.
- **Japan's Fifth Generation project**, begun in 1981 to build machines that could converse, translate and reason, missed its goals and ended in 1992. [26]

Notice the shape: the loser was the *hand-written rules* approach (expert systems), not learning. Learning methods kept improving in the background, on small tasks, until data and computers caught up.

:::key-takeaways
- Backpropagation computes how the loss changes with each weight, layer by layer from the output backward. [25]
- Its mathematical roots go back to Leibniz's chain rule (1676) and control theory. [25]
- The second AI winter (about 1987 to 2000) hit rule-based expert systems and special hardware. [26]
:::

:::glossary
- **Backpropagation**: the method for computing the gradient of the loss with respect to every weight by working backward through the network.
- **Gradient**: for each weight, how much the loss changes if the weight changes a little.
- **Chain rule**: the calculus rule for the rate of change of a function built from other functions.
- **Derivative**: the rate at which something changes.
- **Expert system**: software that encodes human experts' knowledge as explicit rules.
- **Brittle**: works in the narrow case it was written for, breaks outside it.
- **LISP machine**: a computer specialised for the LISP language, popular in 1980s AI.
- **Fifth Generation project**: Japan's 1980s national effort to build intelligent machines.
:::
