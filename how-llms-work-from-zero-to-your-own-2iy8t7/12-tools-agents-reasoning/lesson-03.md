---
id: l55
title: "Lab 12: a tool-calling loop"
quiz: quiz-03.yaml
resources: [../resources/lab12-tool-loop.py]
sources: [13]
---
After this lab you will have built and run the loop behind tool use and ReAct, with a scripted stand-in for the model.

A real agent asks a language model what to do next. To keep this lab offline and free, `fake_model` is a **hand-written function that plays the model's role**. Everything else, the parsing, tool execution and feeding the result back, is the real loop.

## Shortcut: the ready-made script

Download `lab12-tool-loop.py` from this lesson's Resources. It uses only the standard library:

```bash
python lab12-tool-loop.py
```

It was run while writing this course.

## What the script does

1. Defines a `calculator` tool that refuses any input except digits, spaces and `+ - * / ( ) .` (it never runs arbitrary text).
2. Starts a transcript with the question "What is 1234 times 5678?".
3. Loops for at most 5 turns: ask `fake_model` for a reply, append it, look for `Final Answer:`, otherwise look for `Action: tool[args]`, run the tool, and append `Observation: ...`. [13]

## What to look for

The test run printed:

```
--- model turn 1 ---
Thought: I should compute this instead of guessing.
Action: calculator[1234 * 5678]
[the program ran calculator and got: 7006652]
--- model turn 2 ---
Thought: I have the result.
Final Answer: 7006652

answer: 7006652
```

Two turns: one to ask for the tool, one to use the result. 1234 × 5678 is indeed 7,006,652.

## Make it real

To use a real model, replace `fake_model` with a call to one (for example the GPT-2 you ran in lab 1 is too weak to follow this format; use an instruction-tuned model). The rest of the script does not change. That is why the loop is the important part.

## Try this

- Change the question's expression to `12 / 0`. What does the tool return, and does the loop survive?
- Change the model's action to a tool that does not exist. What does the loop print?
- Remove the 5-turn cap and make `fake_model` never give a final answer. What happens? Why is the cap there?

:::key-takeaways
- A tool loop is: model reply → parse action → run tool → append observation → repeat, with a turn cap. [13]
- Everything outside the model is ordinary code, which is where validation belongs.
:::

:::glossary
- **Stand-in model (stub)**: a simple function that plays the role of the model in a test.
- **`re` (regular expressions)**: Python's pattern-matching library, used here to parse replies.
- **Turn cap**: a limit on the number of loop iterations.
- **Whitelist check**: allowing only known-safe characters or values.
- **`eval`**: a Python function that runs text as code; dangerous on untrusted input, so the lab checks it first.
:::
