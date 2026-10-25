---
id: l38
title: "GPT-1 to GPT-3: the same idea, bigger"
quiz: quiz-01.yaml
resources: []
sources: [21, 28, 3, 29, 41, 42]
---
After this lesson you can describe how the GPT family grew from 2018 to 2020, and what changed in how the models were released and used.

## A timeline

| Year | Model | What stands out |
| --- | --- | --- |
| 2018 | GPT-1 | OpenAI's first decoder-only GPT [21] |
| 2019 | GPT-2 | Announced 14 February 2019; 1.5 billion parameters; trained on WebText, about 40 GB of text from roughly 8 million documents [28] |
| 2020 | GPT-3 | 175 billion parameters; available only through an API [3][21] |

Each step used essentially the same architecture and objective (lesson 35) with more parameters and more data. GPT-3 is described in its paper as an autoregressive language model with 175 billion parameters, "10x more than any previous non-sparse language model". [3]

## The family in numbers

| Model | Layers | Vector size | Parameters | Context | Training text |
| --- | --- | --- | --- | --- | --- |
| GPT-1 (2018) | 12 | 768 | about 117M | 512 tokens | BooksCorpus, over 7,000 books [41] |
| GPT-2 small / medium / large / XL (2019) | 12 / 24 / 36 / 48 | 768 / 1024 / 1280 / 1600 | 117M / 345M / 762M / 1542M | 1024 tokens | WebText, about 40 GB [42][28] |
| GPT-3 (2020) | 96 | 12288 | 175 billion | not read for this course | 300 billion tokens [3] |

GPT-2's smallest model "is equivalent to the original GPT", and its second smallest to the largest BERT. The GPT-2 paper also used a vocabulary of 50,257 tokens and a larger batch size of 512. [42] The GPT-3 paper trained 8 models from 125 million to 175 billion parameters, "ranging over three orders of magnitude", all on the same 300 billion tokens, with the same architecture as GPT-2 (including pre-normalisation) except for alternating dense and locally banded sparse attention. Its 175B model has 96 layers, a vector size of 12288 and 96 heads. [3]

Two quick calculations with those numbers. GPT-3 saw about 300 billion / 175 billion, or roughly 1.7 tokens per parameter. In lesson 40 you will see that this is far fewer than the roughly 20 per parameter that Chinchilla recommends. And GPT-2's authors noted that even their largest model "still underfits WebText": it had not finished learning from its data. [42]

## What data, and what it meant

GPT-2's training set, WebText, was built from pages linked in Reddit posts with at least 3 karma, with Wikipedia pages removed. [28] This is a pattern that continues: a model's data comes from a filter on the web, and the filter shapes what the model knows and how it is biased (lesson 3).

## A staged release

OpenAI initially withheld GPT-2's source code, citing the risk of malicious use, and gave selected press outlets limited access instead. It released a 774-million-parameter version on 20 August 2019 and the full model on 5 November 2019, saying by then it had "seen no strong evidence of misuse so far". [28] Whether the caution was warranted is debated; the lesson is that how a model is released became part of the story. The 124-million-parameter model you ran in lab 1 is the smallest of the family. [29]

## What GPT-3 changed about use

GPT-3 was available through an API, not as downloadable weights. [21] And as lesson 35 showed, its paper reported that scaling improved few-shot performance: given a handful of examples in the prompt, with no fine-tuning, the model could translate, answer questions and do some arithmetic. [3] The paper also lists limits: few-shot learning still struggled on some datasets, and some benchmarks raised methodological concerns because the web-scale training data may have contained their test material. [3]

:::key-takeaways
- GPT-1 (2018), GPT-2 (2019, 1.5B parameters) and GPT-3 (2020, 175B) are the same recipe at growing scale. [21][28][3]
- GPT-2 was released in stages; GPT-3 only through an API. [28][21]
- Few-shot ability improved with scale, but contamination of benchmarks by web training data is a concern. [3]
:::

:::glossary
- **WebText**: GPT-2's training set, built from web pages linked on Reddit.
- **Karma**: Reddit's score for a post; used as a rough quality filter.
- **Staged release**: publishing a model in steps (smaller versions first).
- **API**: an interface for sending requests to a model hosted by someone else.
- **Weights (released)**: the downloadable model parameters.
- **Contamination**: test questions appearing in the training data, inflating scores.
- **Non-sparse**: a model that uses all its parameters on every input.
:::
