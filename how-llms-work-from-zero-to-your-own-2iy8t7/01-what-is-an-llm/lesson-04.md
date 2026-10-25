---
id: l04
title: "Lab 1: talk to a real language model"
quiz: quiz-04.yaml
resources: [../resources/lab01-gpt2-chat.py]
sources: [29, 30]
---
After this lab you will have run GPT-2 on your own machine, seen the tokens it works on, and watched greedy and sampled generation differ.

This is a hands-on lab. GPT-2 is a small 2019 model, far weaker than today's assistants, which makes it a good specimen: it is the same idea, small enough to run on a laptop. [29]

## Shortcut: the ready-made script

Download `lab01-gpt2-chat.py` from this lesson's Resources, then:

```bash
uv venv && uv pip install torch transformers
python lab01-gpt2-chat.py "The capital of France is"
```

It needs a one-time download of the model (about 0.5 GB) from Hugging Face; after that it runs offline. The script was run while writing this course on Windows with the setup above.

## What the script does

It uses the `transformers` library: load a tokenizer and the `gpt2` model, turn your prompt into tokens, then call `generate()`. [30] Two settings from the library's documentation matter here. First, `generate()` returns only about 20 new tokens unless you set `max_new_tokens`, so the script sets it. Second, the default way of choosing the next token is *greedy*: always take the most likely one. Greedy suits tasks like translation, but not creative writing, so you can switch on *sampling*, where the next token is drawn at random in proportion to its probability, and use `temperature` to control how adventurous the draw is. [30]

## What to look for

In a test run with the prompt "The capital of France is":

- The tokens printed were `['The', 'Ġcapital', 'Ġof', 'ĠFrance', 'Ġis']`. GPT-2's tokenizer writes a leading space as the character `Ġ`, so "capital" with a space before it is a different token from "capital" at the start of a text. Lesson 20 returns to this.
- Greedy decoding looped: it repeated "the capital of the French Republic" several times. Always picking the single most likely token tends to loop.
- Sampling at temperature 0.9 answered "Paris", then wandered into an unrelated news sentence.

Your output will differ somewhat across library versions, but the pattern (loops when greedy, drift when sampled) should show up.

## Check yourself

- Try three different prompts. When does the model sound right, and when does it sound right but say something false?
- Raise and lower `temperature` (try 0.3 and 1.5). What changes?
- Why does the model's answer to a factual question sometimes start well and then drift? Link your answer to lesson 3.

:::low-confidence
Outputs depend on the library version and random seed; the numbers and sentences above are from one run. The model card also warns that GPT-2 reflects biases of its training data, so do not use its output for anything that matters. [29]
:::

:::key-takeaways
- A language model sees tokens, not words; GPT-2 marks a leading space with `Ġ`. [30]
- Greedy decoding picks the most likely token each step; sampling with a temperature adds variety. [30]
- Set `max_new_tokens`; the default is only about 20. [30]
:::

:::glossary
- **GPT-2**: a 2019 language model with 124 million parameters in its smallest public version, used here as a small specimen.
- **Hugging Face / `transformers`**: a hub of models and the Python library for loading and running them.
- **Tokenizer**: the code that turns text into tokens and back.
- **`generate()`**: the `transformers` function that produces text one token at a time.
- **Greedy decoding**: always choose the most likely next token.
- **Sampling**: choose the next token at random, weighted by its probability.
- **Temperature**: a setting that makes sampling more adventurous (high) or more cautious (low).
- **`max_new_tokens`**: the maximum number of tokens to generate.
- **`uv`**: a fast tool for creating Python environments and installing packages.
:::
