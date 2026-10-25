---
id: l12
title: "LSTM: giving networks a memory (1997)"
quiz: quiz-02.yaml
resources: []
sources: [27, 39]
---
After this lesson you can explain why plain recurrent networks forget, and how the LSTM was designed to remember.

## Text arrives in order

A sentence is a sequence, and what a word means depends on earlier words. A **recurrent neural network (RNN)** handles this by processing one token at a time and carrying a summary of what it has read so far (a hidden state) from step to step. At each step it combines the new token with that summary.

## The vanishing-gradient problem

Training an RNN with backpropagation means sending the error signal back through every step of the sequence. The 1997 LSTM paper opens by saying that learning to store information over long intervals by recurrent backpropagation "takes a very long time, mostly because of insufficient, decaying error backflow". Error signals flowing backward in time tend to either blow up or vanish, and how they change depends exponentially on the size of the weights. [39] This is the **vanishing gradient problem** (and its opposite, the exploding one). Hochreiter's 1991 analysis was the first to describe it. [39][27]

## The LSTM

Sepp Hochreiter and Jürgen Schmidhuber introduced the **long short-term memory** unit in a 1997 paper in *Neural Computation*; an early version circulated as a 1995 technical report. [39][27] Their abstract describes the design: a gradient-based method that, by "enforcing constant error flow through constant error carousels within special units", can learn to bridge time lags of more than 1000 discrete steps. "Multiplicative gate units learn to open and close access to the constant error flow." [39]

In plain words, each unit has a memory cell whose content is carried forward almost unchanged, so the error signal can travel back through it without shrinking. Gates, small learned controls that multiply a signal by a number between 0 and 1, decide when new information may enter the cell and when its content may leave. The abstract adds that LSTM is local in space and time, with computational cost per time step and weight of O(1), and that in their experiments it solved long-time-lag tasks that earlier recurrent algorithms had not, with many more successful runs and much faster learning. [39] LSTMs can still suffer from exploding gradients. [27]

## Where LSTMs were used

LSTMs learned grammatical dependencies such as keeping track of a subject's gender and number across a sentence, and they powered machine translation (Google's 2016 system reportedly cut translation errors by 60%), speech recognition (Google Voice in 2015, Apple's Siri), and other text-prediction tasks. [27]

## What was still wrong

An LSTM, like any RNN, reads a sequence one step at a time. Each step must wait for the one before it, so training cannot be spread across many chips at once, and everything the network knows about the past must be squeezed through one hidden state. Lesson 29 shows how the next idea, attention, attacked this second problem. A 2020 study found that Transformers scale better than LSTMs on text. [27]

:::low-confidence
Only the abstract and introduction of the 1997 paper were read. The "wait for the previous step" limitation above is the standard explanation of why recurrent networks train slowly on modern hardware; the Transformer paper's comparison table states it directly (lesson 31). [39]
:::

:::key-takeaways
- RNNs process text step by step and carry a summary forward; their error signals can vanish over long sequences. [27]
- The LSTM (Hochreiter and Schmidhuber, 1997) keeps error signals alive with a "constant error carousel" and learned gates, bridging lags of over 1000 steps. [39]
- LSTMs drove translation and speech recognition before Transformers. [27]
:::

:::glossary
- **RNN (recurrent neural network)**: a network that reads a sequence one step at a time, carrying a hidden state forward.
- **Hidden state**: the summary of what has been read so far.
- **Vanishing gradient**: the error signal shrinking toward zero over many steps, so early steps stop learning.
- **Exploding gradient**: the opposite: the signal growing without bound.
- **LSTM (long short-term memory)**: an RNN design with gates that keep useful information over many steps.
- **Gate**: a learned control that decides how much information passes through.
- **Constant error carousel**: the LSTM path that lets the error signal persist without shrinking.
- **Sequence**: items in a fixed order, such as the tokens of a sentence.
:::
