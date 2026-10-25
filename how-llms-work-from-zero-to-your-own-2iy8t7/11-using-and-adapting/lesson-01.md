---
id: l48
title: Prompting and in-context learning
quiz: quiz-01.yaml
resources: []
sources: [3, 30]
---
After this lesson you can explain why a prompt can teach a model a task with no training, and write a prompt with a role, examples and a format.

## Learning without changing a single weight

The GPT-3 paper's most surprising result: scale up a language model enough and it can do a task given only a few examples written into the prompt, with no gradient updates or fine-tuning at all. Tasks and demonstrations are specified purely through text. [3] This is **in-context learning**, and a handful of examples in the prompt is **few-shot** prompting. The paper reports good performance this way on translation, question answering, cloze tasks, and tasks requiring on-the-fly reasoning such as unscrambling words and three-digit arithmetic. [3]

Nothing is stored. The "learning" lasts as long as the examples stay in the context window (lesson 2) and vanishes when they leave.

## The parts of a good prompt

A prompt is the only way you steer the model, so structure helps. Common parts:

1. **Role or situation**: who the model is acting as, and for whom.
2. **The task**, stated plainly.
3. **Examples** (few-shot): two to five inputs with the exact outputs you want.
4. **The input** to process now.
5. **The output format**: for example "reply as JSON with the keys `label` and `reason`".

Example:

```
You classify support tickets as BILLING, BUG or OTHER. Reply with one word.

Ticket: "I was charged twice this month." -> BILLING
Ticket: "The export button does nothing." -> BUG
Ticket: "Do you have a student discount?" ->
```

The model continues the pattern. The examples teach both the task and the exact output format.

## Practical points

- **Chat models expect their template.** The Hugging Face documentation warns that a chat model passed a single plain string rather than its role-structured template may return suboptimal output. [30]
- **Decoding matters.** For classification or extraction use greedy decoding or low temperature; creative tasks use higher. [30]
- **Prompts are fragile.** Small wording changes can change results. Treat prompts as code: version them and test them against fixed examples (chapter 13).
- **Examples can mislead.** The model copies patterns in them, including accidental ones such as always answering with the first option.

:::key-takeaways
- Large models can learn a task from a few examples in the prompt, with no weight updates (in-context, few-shot learning). [3]
- A good prompt has a role, a task, examples, the input and an output format.
- Use the model's chat template, and lower temperature for deterministic tasks. [30]
:::

:::glossary
- **Prompt**: the text you give the model to continue.
- **In-context learning**: learning a task from examples inside the prompt, with no weight changes.
- **Zero-shot / few-shot**: no examples / a few examples in the prompt.
- **Demonstration**: one example input with its desired output.
- **Output format**: the exact shape of reply you ask for (a word, JSON, a list).
- **Chat template**: the role-structured layout a chat model was trained on.
- **Cloze task**: filling in a blank in a sentence.
:::
