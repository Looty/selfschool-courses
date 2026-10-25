---
id: l35
title: Decoder-only GPT, and the BERT alternative
quiz: quiz-02.yaml
resources: []
sources: [9, 21, 3, 28, 41, 68, 69]
---
After this lesson you can say what "decoder-only" means, how GPT differs from BERT, and why next-token prediction became the dominant way to train.

## From the translation Transformer to GPT

The 2017 Transformer was built for translation, with an encoder and a decoder. Two kinds of language model came from taking one half.

- **Encoder-only: BERT (October 2018).** BERT pre-trains deep *bidirectional* representations from unlabelled text, using both left and right context in all layers. A pretrained BERT is then fine-tuned with one extra output layer for a task, and it reported new state-of-the-art results on eleven NLP tasks, for example a GLUE score of 80.5%. [9] It sees the whole sentence at once, which suits understanding tasks such as classification.
- **Decoder-only: GPT (2018 onward).** GPT-1 was a decoder-only model released by OpenAI in 2018, followed by GPT-2 in 2019, which was announced on 14 February 2019 and has 1.5 billion parameters in its largest version. [21][28] A decoder-only model sees only the tokens to the left (the causal mask of lab 7) and predicts the next one.

Wikipedia's overview notes that academic use of BERT started to decline from 2023 as prompted decoder-only models improved. [21]

## GPT-1 in numbers

The first GPT paper, "Improving Language Understanding by Generative Pre-Training" (Radford, Narasimhan, Salimans and Sutskever, OpenAI, 2018), is short enough to summarise completely. [41]

- **Idea:** large unlabelled text corpora are abundant while labelled data for specific tasks is scarce. So first do *generative pre-training* of a language model on unlabelled text, then *discriminative fine-tuning* on each task, using task-aware input transformations so the architecture barely changes. [41]
- **Model:** a 12-layer decoder-only Transformer with masked self-attention, 768-dimensional states, 12 attention heads and 3072-dimensional feed-forward inner states. It used GELU activations, learned position embeddings (not the sinusoidal ones), BPE with 40,000 merges, and dropout of 0.1. [41]
- **Data:** BooksCorpus, over 7,000 unique unpublished books, chosen because it "contains long stretches of contiguous text, which allows the generative model to learn to condition on long-range information". A shuffled-sentence alternative would destroy that structure. [41]
- **Training:** the Adam optimiser, 100 epochs on minibatches of 64 sequences of 512 contiguous tokens, a learning rate warmed up linearly over the first 2000 updates and then annealed with a cosine schedule. [41]
- **Result:** one general model beat task-specific architectures on 9 of 12 tasks, for example +8.9% on commonsense reasoning (Stories Cloze Test), +5.7% on question answering (RACE) and +1.5% on textual entailment (MultiNLI). [41]

GPT-1 is the template for everything after it: pre-train on a lot of text, then adapt. BERT (2018) took the same path with an encoder, and ELMo and ULMFiT (lesson 61) had shown earlier in 2018 that pretrained language models transfer. [9][68][69]

## Why next-token prediction won

The training task for a decoder-only model is just: predict each next token of ordinary text. That has big advantages.

- **Free labels.** The right answer for every position is the next token of the text itself, so any text can be training data. No human labelling is needed.
- **One task, many uses.** A model that is good at continuing text can also answer, translate or summarise if the prompt is phrased as a text to continue. The GPT-3 paper showed this: with 175 billion parameters it performed tasks from a few examples in the prompt, with no fine-tuning ("few-shot"), approaching earlier fine-tuned methods on some. [3]
- **Generation is built in.** The same loop that trains it (predict next token) is the loop that writes (lesson 2).

## Shapes of the full network

A decoder-only GPT is:

```
token ids -> token embedding + position embedding
          -> N Transformer blocks (masked self-attention + feed-forward, with residuals and normalisation)
          -> final normalisation -> a linear layer giving one score (logit) per vocabulary token
          -> softmax -> probabilities for the next token
```

That is the entire architecture. The mini-GPT in the lab is exactly this, in about 120 lines.

:::key-takeaways
- BERT is encoder-only and bidirectional; GPT is decoder-only and reads left to right. [9][21]
- Next-token prediction needs no labelling: the next token of any text is the answer. 
- The GPT-3 paper showed that scaling this simple objective gives strong few-shot performance. [3]
:::

:::glossary
- **Encoder-only (BERT)**: a model that reads the whole sentence in both directions to build representations.
- **Decoder-only (GPT)**: a model that reads left to right and predicts the next token.
- **Bidirectional**: using context from both sides.
- **Self-supervised**: learning from labels that come from the data itself, such as the next token.
- **Few-shot**: giving a handful of examples in the prompt, with no extra training.
- **GLUE**: a collection of language-understanding tests.
- **Logit**: the raw score for one token before softmax.
:::
