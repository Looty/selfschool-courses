---
id: l49
title: "Chain-of-thought: letting the model show its work"
quiz: quiz-02.yaml
resources: []
sources: [12, 21]
---
After this lesson you can explain chain-of-thought prompting, when it helps, and what it does and does not prove.

## The finding

Ask a model a multi-step word problem and it may blurt a wrong number. In January 2022 Wei and colleagues showed that prompting the model to write out **intermediate reasoning steps** improves its performance on complex reasoning. The method is simple: include a few worked examples in the prompt that show step-by-step reasoning, with no fine-tuning. [12]

Results: gains across arithmetic, commonsense and symbolic reasoning tasks on three large language models. A 540-billion-parameter model prompted with eight such examples reached state-of-the-art accuracy on GSM8K, a benchmark of math word problems, outperforming a fine-tuned GPT-3 combined with a verifier. [12]

The paper also finds that these reasoning abilities emerge in sufficiently large language models: the technique helped large models far more than small ones. [12]

## Why would it help?

A model produces one token at a time and cannot "think silently" for longer on a harder problem: each token gets the same amount of computation. Writing intermediate steps gives it a scratchpad. Each step's tokens become part of the context for the next, so a hard problem is split into several easy ones. (This is the common explanation for the effect, not a claim quoted from the paper's abstract.)

## An example

```
Q: Roger has 5 tennis balls. He buys 2 cans of 3 balls each. How many balls now?
A: Roger started with 5 balls. 2 cans of 3 balls is 6 balls. 5 + 6 = 11. The answer is 11.
```

Giving a few examples like this, then a new question, makes the model write its own steps before the final answer.

## What it does not prove

The written steps look like reasoning, but a fluent explanation is not a guarantee of a correct one: a model can write plausible steps that lead to a wrong answer, or a right answer with flawed steps. The same ELIZA-effect caution applies (lesson 8). Check the final answer, not how convincing the steps sound.

## Where it led

Reasoning-trained models now produce long chains of thought before answering by default: OpenAI's o1 (2024) and DeepSeek-R1 (a 671-billion-parameter open-weight model, January 2025) are examples named in Wikipedia's overview, and lesson 56 returns to them. [21]

:::key-takeaways
- Prompting a model to write out intermediate steps improves complex reasoning, without fine-tuning. [12]
- The effect emerges in large models; a 540B model with eight examples set a GSM8K record at the time. [12]
- Fluent steps are not proof of correct reasoning; check the answer.
:::

:::glossary
- **Chain of thought**: intermediate reasoning steps written out before the final answer.
- **GSM8K**: a benchmark of grade-school math word problems.
- **Emergent ability**: a skill that appears only in sufficiently large models.
- **Scratchpad**: space to write working before answering.
- **Verifier**: a separate model or check that rates candidate answers.
- **Reasoning model**: a model trained to produce long chains of thought before answering.
:::
