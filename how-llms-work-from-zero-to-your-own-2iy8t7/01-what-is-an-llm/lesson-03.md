---
id: l03
title: What an LLM gets wrong
quiz: quiz-03.yaml
resources: []
sources: [21, 29, 37, 4]
---
After this lesson you can name the main ways LLMs fail, and explain why those failures follow from how they are built.

## Fluent is not the same as true

An LLM is trained to produce likely text, not true text. Usually the likely continuation is also the true one, which is why the models are useful. But the training objective never checks facts. The term for a confident statement that the training data does not justify is **hallucination**: the text can read well while being wrong, or unfaithful to a source it was given. [21]

A benchmark built to probe this, TruthfulQA, has 817 questions across 38 categories, written so that some people would answer falsely because of a common misconception. The best model tested was truthful on 58% of questions, against 94% for humans, and the largest models were generally the least truthful, because they had learned popular falsehoods from their training text. The authors argued that making models bigger is less promising for truthfulness than training them with objectives other than imitating web text. [37]

## It repeats the data it was trained on

If the training text contains a stereotype, the model can reproduce it. The model card for GPT-2, a small early model you will run in the next lesson, says the model cannot tell fact from fiction, reflects the biases of its training data, and shows an example where completions for two prompts that differ only in a person's race differ in stereotyped ways. [29] Fine-tuned versions inherit this. [29]

## Bigger does not mean it does what you ask

The InstructGPT paper starts from the observation that scaling a language model up does not by itself make it better at following what the user wants: large models can still produce untruthful, toxic or unhelpful output. [4] That is the reason models are tuned after pretraining, which chapter 10 covers.

## Limits that come with the design

- **Black box.** It is unclear how LLMs perform language tasks internally. [21]
- **Cost.** Training the largest models needs large infrastructure; the same overview puts GPT-2 (2019) at about $50,000 and PaLM (2022) at about $8 million. [21]
- **A window, not a memory.** It only sees what fits in its context window (lesson 2).

:::low-confidence
The cost figures are from an encyclopedia overview, not from a primary source, and training costs depend on hardware and pricing at the time. Treat them as orders of magnitude. [21]
:::

## What to do about it

Treat an LLM's output as a draft from a fast, widely read, occasionally overconfident colleague. Check anything that matters, give it the source text to work from when accuracy counts (chapter 11 shows how), and measure it on your own questions (chapter 13).

:::key-takeaways
- Hallucination: fluent text the training data does not justify. [21]
- Larger models were generally less truthful on TruthfulQA; scale alone does not fix truthfulness. [37]
- Models reflect biases in their training data. [29]
- Scaling up does not by itself make a model follow user intent. [4]
:::

:::glossary
- **Hallucination**: a confident statement from a model that its training data does not justify.
- **Benchmark**: a fixed set of test questions used to compare models.
- **TruthfulQA**: a benchmark of questions where common misconceptions lure models into false answers.
- **Bias (in data)**: a systematic skew in the training text that a model can copy.
- **Model card**: a short document describing a model's intended use and limits.
- **Toxic output**: harmful, abusive or offensive text.
- **Black box**: a system whose internal workings are hard to inspect.
- **Objective**: what a model is trained to do; here, predict likely text.
:::
