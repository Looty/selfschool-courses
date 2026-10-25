---
id: l10
title: The perceptron, XOR and the first AI winter
quiz: quiz-06.yaml
resources: []
sources: [24, 26]
---
After this lesson you can explain what the perceptron was, what it could not do, and why AI funding collapsed in the 1970s.

## A machine that learns weights

Rosenblatt's perceptron is the first neuron-like learner. Frank Rosenblatt, at the Cornell Aeronautical Laboratory, simulated it on an IBM 704 in 1957 and described it in a 1958 paper. [24] Instead of a person writing rules, the perceptron adjusts numbers (weights) from examples until it classifies them correctly. This is the second answer from lesson 6: learn the rules from data.

He also built hardware. The Mark I Perceptron, built in 1959 and first demonstrated on 23 June 1960, took a 20 by 20 grid of 400 photocells as input, and used motors to turn potentiometers that held the adjustable weights. It was designed for image recognition. [24]

## The limit: XOR

In 1969 Marvin Minsky and Seymour Papert's book *Perceptrons* showed that a **single-layer** perceptron can only learn patterns that are *linearly separable*, meaning a straight line (or flat plane) can separate the classes. It cannot learn XOR ("exclusive or": true when exactly one of two inputs is true). [24]

A common misreading is that the book showed *multilayer* networks had the same limit. It did not, and the article notes the book is often miscited that way. Its influence nonetheless contributed to a decline in neural-network research until the 1980s. [24]

## The first AI winter

An **AI winter** is a period of cut funding and lost interest after hype outruns results. The first, roughly 1974 to 1980, had several causes. [26]

- **The Lighthill report (1973)**, commissioned by the UK Parliament, found AI had fallen short of its "grandiose objectives" and warned that many algorithms worked only on toy problems because of combinatorial explosion. UK AI research was largely dismantled. [26]
- **A shift in US funding.** The 1969 Mansfield Amendment required DARPA to fund mission-oriented work, and overpromising had frustrated the agency; in 1974 it cancelled a speech-understanding contract at Carnegie Mellon after feeling misled. [26]

The historian Thomas Haigh disputes that this was a true winter, pointing out that the number of researchers kept growing. [26] Treat "winter" as a convenient label for a real funding shock, not as proof that all work stopped.

## The pattern to remember

Hype, then disappointment, then a quieter period in which useful ideas keep developing. The next chapter picks up the idea that was waiting: multilayer networks and a practical way to train them.

:::key-takeaways
- The perceptron (Rosenblatt, 1958) learns weights from examples. [24]
- A single-layer perceptron cannot learn XOR; the 1969 book *Perceptrons* showed this, and it is wrongly cited as a limit of multilayer networks. [24]
- The first AI winter (roughly 1974 to 1980) followed overpromising and funding cuts, including the 1973 Lighthill report; a historian disputes how real it was. [26]
:::

:::glossary
- **Perceptron**: the earliest neuron-like learning machine; it adds up weighted inputs and decides yes or no.
- **Weight**: a number saying how much one input counts.
- **Single-layer**: has only one layer of adjustable weights between input and output.
- **Linearly separable**: classes that a straight line can separate.
- **XOR (exclusive or)**: true when exactly one of two inputs is true.
- **Multilayer network**: stacked layers of neurons; it can learn patterns a single layer cannot.
- **AI winter**: a period of reduced funding and interest in AI.
- **DARPA**: the US defence research agency that funded much early AI.
- **Combinatorial explosion**: the number of possibilities growing too fast to search.
:::
