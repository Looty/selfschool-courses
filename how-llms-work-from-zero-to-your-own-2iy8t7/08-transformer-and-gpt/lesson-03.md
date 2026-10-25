---
id: l36
title: "Lab 8: train a mini-GPT on your CPU"
quiz: quiz-03.yaml
resources: [../resources/minigpt.py, ../resources/lab-corpus.py, ../resources/lab08-train-mini-gpt.py]
sources: [17, 1]
---
After this lab you will have trained a 112,577-parameter GPT on Shakespeare in about a minute and watched it go from random characters to something English-shaped.

## Shortcut: the ready-made scripts

Download `minigpt.py`, `lab-corpus.py` and `lab08-train-mini-gpt.py` from this lesson's Resources, into one folder:

```bash
uv venv && uv pip install torch numpy
python lab-corpus.py                  # creates input.txt (skip if you already ran it)
python lab08-train-mini-gpt.py        # 1000 steps, about 1 minute
python lab08-train-mini-gpt.py 4000   # more steps, lower loss
```

All three scripts were run while writing this course on a laptop CPU.

## What the model is

`minigpt.py` is the architecture of lessons 33 to 35 in about 120 lines, character-level to keep it small: 65 distinct characters in the vocabulary (no BPE, to keep the focus on the model), a context window of 64 characters, 2 blocks, 4 attention heads and 64 numbers per token. That adds up to **112,577 parameters**. The design follows the Transformer; the scale and the character-level text are simplifications in the same spirit as nanoGPT's character-level Shakespeare example. [1][17]

## What to look for

1. **Before training**, with random weights, the model's output is random characters. Its loss is about 4.33, which is the uniform-guess value (log of 65 is 4.17) plus a little.
2. **During training**, the loss on held-out text falls fast. In the test run: 4.334 at step 0, 2.279 at step 250, 2.082 at step 500, 1.973 at step 750, and **1.932 at step 1000**, in 36 seconds.
3. **After training**, the output has line breaks, speaker names in capitals followed by a colon, and word-like clumps:

```
GLOUCESTER:
Henespith the with not sunot with in eards, my father hand
lian a chontempost on the morefold himes offor the am the parcince there a ve
```

Compare with the bigram of lab 6 (loss 2.493, no sense at all): attention over 64 characters of context already produces the format of a play and some real words, with a loss of 1.93.

## Try this

- Run it with 4000 steps. How low does the loss go? What improves in the text?
- In `lab08-train-mini-gpt.py` change `Config()` to `Config(n_layer=1)` or `Config(n_embd=32)`. Which change hurts more?
- Print the number of parameters for each variation. How is it split between the embedding table, the attention and the feed-forward layers?

## Check yourself

- Where in `minigpt.py` is the causal mask? Which line applies it?
- The model never saw any grammar rules. What taught it that a character name is followed by a colon?

:::key-takeaways
- A complete GPT is about 120 lines; the mini version trains on a laptop CPU in a minute. [1]
- Held-out loss went from 4.33 (random) to 1.93 (trained) in 1000 steps; the bigram scored 2.49.
- Structure like speaker names and line breaks is learned from the statistics of text alone.
:::

:::glossary
- **PyTorch**: the Python library for building and training neural networks.
- **Character-level model**: one whose tokens are single characters.
- **Context length / block size**: how many tokens the model sees at once; 64 in the lab.
- **Step**: one update of the weights from one batch of examples.
- **Batch**: a group of training examples processed together.
- **AdamW**: a popular optimiser, a refined version of gradient descent.
- **Checkpoint (`mini-gpt.pt`)**: the saved weights of a trained model.
:::
