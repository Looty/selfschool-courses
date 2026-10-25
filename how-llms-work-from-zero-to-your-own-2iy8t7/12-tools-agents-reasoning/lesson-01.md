---
id: l53
title: "Tool use: models that call programs"
quiz: quiz-01.yaml
resources: []
sources: [21, 13, 57]
---
After this lesson you can explain how a text-only model can use a calculator or a search engine, and where the risks lie.

## A model can only write text

A language model produces tokens. It cannot look up today's weather, run code or query a database. But text can describe an action, and a separate program can carry it out. Wikipedia's overview describes tool use this way: a separate program watches the model's output for tool-calling syntax, runs the tool, and feeds the result back to the model. [21]

## The loop

1. The prompt describes the tools available and the format for calling them (for example `calculator[1234 * 5678]`).
2. The model writes a reply. If it wants a tool, it writes a call in that format and stops.
3. The surrounding program spots the call, runs the tool, and appends the result to the conversation.
4. The model is run again, now with the result in its context, and continues, possibly calling more tools, until it writes a final answer.

The model never executes anything. Everything that touches the outside world is done by your program, which makes it the place to put checks.

## Why it helps

Models are good at language and unreliable at exact arithmetic, current facts and long computations (lesson 3). Tools cover those gaps. The ReAct paper's experiments used a simple Wikipedia API as the external tool and found that using it reduced the hallucination and error propagation that affected pure chain-of-thought reasoning on question-answering. [13]

## Teaching the model when to call: Toolformer

In the ReAct pattern the tool format is described in the prompt. Toolformer (Schick et al., February 2023) asked whether models can *learn* tool use. The paper starts from the observation that language models do well at many tasks yet stumble on simple ones such as arithmetic or factual lookup, where much smaller specialised systems excel. Toolformer is trained, in a self-supervised way and with only a handful of demonstrations per API, to decide which APIs to call, when to call them, what arguments to pass and how to incorporate the results into later token prediction. [57] Its tools included a calculator, a question-answering system, two search engines, a translation system and a calendar, and it improved zero-shot performance across tasks, often matching much larger models, without losing its core language-modelling ability. [57]

## Risks to design for

- **The model decides what to call.** Treat its output as untrusted input. Validate arguments (the lab only lets the calculator see digits and operators).
- **Cap the loop.** A model can call tools forever; set a maximum number of turns.
- **Least privilege.** Give a tool only the access it needs. A tool that can send email or delete files is a risk if the model can be misled by text it reads.
- **Text in tool results is also prompt text.** A web page the model reads can contain instructions aimed at it. (The MLOps course in this app discusses prompt injection.)

:::key-takeaways
- Tool use = the model writes a structured call, your program runs it and feeds the result back. [21]
- It covers weaknesses of LLMs: exact maths, current facts, long computation. [13]
- Treat the model's calls as untrusted: validate, cap turns, limit privileges.
:::

:::glossary
- **Tool use / function calling**: the model asks, in a set format, for a program to run, and receives the result.
- **Tool**: a program the model can ask for, such as a calculator or search.
- **Tool-calling syntax**: the exact text format the model uses to request a tool.
- **Observation**: the result of a tool call, fed back into the conversation.
- **Least privilege**: giving a component only the access it needs.
- **Prompt injection**: instructions hidden in text the model reads, trying to hijack its behaviour.
- **Untrusted input**: data you must check because you do not control its source.
:::
