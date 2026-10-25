---
id: l56
title: Reasoning models
quiz: quiz-04.yaml
resources: []
sources: [21, 12, 53]
---
After this lesson you can say what a reasoning model is, how it differs from a model prompted with chain-of-thought, and what it costs.

## From a prompt trick to a trained behaviour

Chain-of-thought (lesson 49) was a prompting technique: show worked examples and the model writes steps. A **reasoning model** is one trained so that it produces long chains of thought before answering as its normal behaviour. Wikipedia's overview describes them as models trained to produce step-by-step analysis before final answers, which helps on math, coding and logic tasks but requires more compute per query. [21]

Two examples named there: OpenAI's o1, released in 2024, which generates long chains of thought before answering; and DeepSeek-R1, a 671-billion-parameter open-weight reasoning model released in January 2025, followed by OpenAI's o3 in April 2025. [21]

## What DeepSeek-R1 says about how they are made

DeepSeek-R1's authors state the idea in the abstract: "the reasoning abilities of LLMs can be incentivized through pure reinforcement learning (RL)", obviating the need for human-labelled reasoning trajectories. Instead of showing the model human-written chains of thought, the training rewards correct final answers on tasks that can be checked automatically (the paper names mathematics, coding competitions and STEM fields). The abstract reports that this RL framework leads to emergent reasoning patterns such as self-reflection, verification and dynamic strategy adaptation, that the model performs strongly on verifiable tasks and outperforms counterparts trained with supervised learning on human demonstrations, and that reasoning patterns from large models can be used to improve smaller models. The work was published in *Nature* in 2025 (volume 645). [53]

This is the same loop as RLHF (lesson 44) with a different reward: a program that checks the answer, rather than a model trained on human preferences. It works where answers can be verified, such as maths or code with tests; it is less obviously applicable where "correct" is a matter of taste.

:::low-confidence
Only the abstract of the DeepSeek-R1 paper was read, and the o1 and o3 details come from an encyclopedia overview, not from their own reports. The paper's training recipe (for example how much supervised data it also used) and its results tables are not covered here. [53][21]
:::

## Why it can help

The explanation from lesson 49 carries over. Each generated token gets a fixed amount of computation, so letting the model write more tokens before committing to an answer gives it more computation to spend on a hard problem. Writing intermediate steps also lets it check and revise, and a trained model can learn to do that. [12]

## What it costs

- **More tokens per answer**, so higher latency and cost per query. [21]
- **Visible reasoning can mislead.** As lesson 49 said, plausible steps do not guarantee a correct answer. [12]
- **Not always better.** For simple lookups and rewriting, a plain model is faster and cheaper.

## Choosing

Use a reasoning model for multi-step problems where correctness matters and latency is acceptable: maths, code, planning. Use a plain model for fast, simple tasks. Test both on your own cases (chapter 13).

:::key-takeaways
- Reasoning models are trained to produce long step-by-step thinking before answering. [21]
- They help on math, code and logic but use more compute per query. [21]
- Plausible reasoning is not proof of correctness; test on your own cases. [12]
:::

:::glossary
- **Reasoning model**: a model trained to write long chains of thought before its answer.
- **o1 / o3 (OpenAI), DeepSeek-R1**: examples of reasoning models. [21]
- **Open-weight**: the trained parameters are published for others to download and run.
- **Inference-time compute**: computation spent while answering, not while training.
- **Latency**: how long an answer takes.
- **Chain of thought**: written intermediate reasoning steps.
:::
