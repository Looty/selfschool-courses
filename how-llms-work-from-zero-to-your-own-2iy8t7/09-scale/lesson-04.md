---
id: l41
title: What training costs, and where the data comes from
quiz: quiz-04.yaml
resources: []
sources: [18, 21, 28, 11, 3]
---
After this lesson you can give orders of magnitude for training cost, and describe the sources and risks of training data.

## Cost, then and now

Training cost depends on hardware and prices, so quote numbers with their year. Wikipedia's overview puts the cost of training GPT-2 in 2019 at about $50,000 and of PaLM in 2022 at about $8 million. [21] The nanochat README gives a very different data point on the cheap end: a GPT-2-class model that it can train in about 2 hours on a single node of 8 H100 GPUs, costing about $48 at on-demand prices (around $3 per GPU-hour) or about $15 on spot instances. It compares this with about $43,000 for training GPT-2 in 2019. [18] The project's stated goal is to keep end-to-end small-model training under $1000. [18]

:::low-confidence
These cost figures come from an encyclopedia overview and a project's own README. They use different accounting (the README's compares like with like only loosely), and prices change. Use them as orders of magnitude: tens of thousands of dollars in 2019, tens of dollars with newer code and hardware for the same capability class. [21][18]
:::

## Where the data comes from

GPT-2's WebText was about 40 GB of text from roughly 8 million documents, built from pages linked on Reddit with at least 3 karma, with Wikipedia removed. [28] LLaMA's authors state that state-of-the-art models can be trained using publicly available datasets exclusively, and trained on trillions of tokens. [11] The more data a model sees, the more it needs diverse and clean data, and the more its quality depends on filtering.

Risks that come with web-scale data:

- **Bias and falsehoods** are learned along with facts (lesson 3).
- **Contamination:** benchmark questions may appear in the training text, inflating scores. [3]
- **Copyright and privacy** questions about what text may be used (not covered by these sources).

## Why this matters for your own experiments

You do not need to train a frontier model to learn the field. The labs in this course train models with about 10,000 to 800,000 parameters, in seconds to minutes, on a laptop. The ratios are the same ones the scaling-law papers study: parameters, tokens, loss.

:::key-takeaways
- Training cost fell by orders of magnitude for the same capability class between 2019 and recent open code. [21][18]
- Data comes from web-scale filtered text; its biases and contamination matter. [28][11]
- You can study scaling at laptop size.
:::

:::glossary
- **GPU-hour**: one GPU used for one hour; the usual unit of training cost.
- **H100 / A100**: data-centre GPUs from NVIDIA.
- **Spot instance**: cheaper cloud machines that can be taken away at short notice.
- **Corpus**: the collection of text used for training.
- **Filtering**: removing low-quality or unwanted text from the corpus.
- **Public dataset**: text anyone can download, as opposed to private data.
- **Contamination**: test material leaking into training data.
:::
