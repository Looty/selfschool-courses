---
id: l54
title: "ReAct: reasoning and acting together (2022)"
quiz: quiz-02.yaml
resources: []
sources: [13]
---
After this lesson you can describe the ReAct pattern and what makes an "agent" different from a single prompt.

## Two ideas, joined

By late 2022 there were two separate lines of work with language models. One made models **reason** by writing steps (chain-of-thought, lesson 49). The other made models **act**, for example by generating plans or calling tools. The ReAct paper (Yao et al., October 2022) argued the two belong together and proposed generating reasoning traces and task-specific actions in an **interleaved** manner. [13]

The reasoning helps the model "induce, track, and update action plans as well as handle exceptions", and the actions let it gather information from external sources such as knowledge bases or environments. [13]

## The pattern

A ReAct transcript alternates three kinds of line:

```
Thought: I need the population of France; I should search.
Action: search[population of France]
Observation: (result text returned by the program)
Thought: The result says ... so the answer is ...
Final Answer: ...
```

- **Thought**: the model reasons in text.
- **Action**: a tool call in a fixed format.
- **Observation**: written by your program, not by the model.

The loop ends when the model writes a final answer. The next lab implements exactly this loop.

## What the paper found

On HotpotQA (multi-step question answering) and FEVER (fact verification), a simple Wikipedia API reduced the hallucination and error propagation that affect chain-of-thought alone. The authors also say the task-solving trajectories are more interpretable than those of baselines without reasoning traces. On the interactive environments ALFWorld and WebShop, ReAct outperformed imitation and reinforcement-learning methods by absolute success rates of 34% and 10%, using only one or two in-context examples. [13]

## From pattern to agent

An **agent** is a program that runs a loop like this: observe, decide with a model, act with tools, repeat until a goal is met. All the pieces come from earlier lessons: the model predicts text (chapter 8), the prompt explains the format (lesson 48), the program parses and executes calls (lesson 53). What makes agents risky is that errors compound over many steps; one wrong action can mislead everything after it, so evaluation of whole trajectories, not single answers, matters (chapter 13).

:::key-takeaways
- ReAct interleaves reasoning traces and actions: Thought, Action, Observation, repeat. [13]
- Reasoning helps plan and handle exceptions; actions bring in outside information. [13]
- On question answering, using a Wikipedia tool reduced hallucination and error propagation compared with chain-of-thought alone. [13]
:::

:::glossary
- **ReAct**: a prompting pattern that interleaves reasoning ("Thought") with tool calls ("Action").
- **Reasoning trace**: the written thinking steps.
- **Trajectory**: the whole sequence of thoughts, actions and observations for one task.
- **Agent**: a program that loops: decide with a model, act with tools, observe, repeat.
- **HotpotQA / FEVER**: benchmarks for multi-step question answering and fact checking.
- **Error propagation**: an early mistake spoiling all later steps.
:::
