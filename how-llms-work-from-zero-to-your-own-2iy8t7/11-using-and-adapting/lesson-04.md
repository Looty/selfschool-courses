---
id: l51
title: "Lab 11: LoRA by hand"
quiz: quiz-04.yaml
resources: [../resources/minigpt.py, ../resources/lab-corpus.py, ../resources/lab08-train-mini-gpt.py, ../resources/lab11-lora.py]
sources: [10]
---
After this lab you will have adapted your trained mini-GPT to a new task by training 3,072 numbers instead of 112,577.

This is a teaching implementation of the idea in the LoRA paper, not the official library. [10]

## Shortcut: the ready-made scripts

Use the folder from lab 8, which must contain `minigpt.py`, `input.txt` and the saved model `mini-gpt.pt` (made by `lab08-train-mini-gpt.py`). Add `lab11-lora.py` from this lesson's Resources:

```bash
python lab08-train-mini-gpt.py    # if you have not already: it saves mini-gpt.pt
python lab11-lora.py              # about 15 seconds
```

It was run while writing this course.

## What the script does

1. Loads the pretrained mini-GPT (lowercase and mixed-case Shakespeare).
2. Builds a new task from the same text: the whole text **in capital letters**. The characters are in the vocabulary, but the model rarely saw them.
3. Replaces each attention projection (`qkv` and `proj`) with a `LoRALinear` that wraps the original layer: the original weights are frozen, and two thin matrices `A` (4 × n_in) and `B` (n_out × 4) are added so the layer computes `W·x + (B·A)·x × scale`. `B` starts at zero, so at the start the model behaves exactly as before. [10]
4. Freezes everything else and trains only `A` and `B` for 500 steps.

## What to look for

In the test run:

- Before fine-tuning, the loss on the all-caps text was **4.466**, worse than guessing uniformly (4.17), because the model was confidently wrong about unfamiliar characters.
- **Trainable parameters: 3,072 of 112,577 (2.7%).**
- After 500 steps of LoRA training the loss fell to **2.323** (2.387 at step 250), and the sample was all-caps text with word-like clumps.

## An honest limit

The result (2.32) is far from the 1.93 the model reached on normal text. The reason is instructive: LoRA touched only the attention matrices. The embedding table (lesson 23) and the feed-forward layers stayed frozen, so the model could not learn new representations for capital letters, which it had barely seen. LoRA works best when the new task is *close* to what the base model already knows. The LoRA paper's study of rank deficiency suggests that useful changes live in few dimensions, but that holds for tasks near the original one. [10]

## Try this

- Change the rank from 4 to 1, then to 16. How do the trainable-parameter count and the final loss change?
- Also wrap the feed-forward layers (`blk.mlp[0]` and `blk.mlp[2]`) in `LoRALinear`. Does the loss improve?
- Fine-tune on a task closer to the original, such as the same text with every `e` replaced by `3`. How does the result compare?

## Check yourself

- Why is `B` initialised to zeros?
- How many numbers would you need to store a separate LoRA for 100 different tasks, compared with 100 full copies of the model?

:::key-takeaways
- LoRA trained 3,072 of 112,577 parameters (2.7%) and cut the all-caps loss from 4.466 to 2.323. [10]
- It is limited by what it can touch: attention-only LoRA could not relearn the embeddings.
- A LoRA file is tiny compared with a full model copy.
:::

:::glossary
- **`LoRALinear`**: the lab's class that wraps a frozen layer with two small trainable matrices.
- **Rank**: the inner size (4 here) of the two thin matrices; higher rank, more capacity.
- **`alpha` / scale**: a multiplier controlling how strongly the LoRA correction is applied.
- **Zero initialisation**: starting `B` at zero so the model starts unchanged.
- **`requires_grad`**: PyTorch's switch for whether a parameter is trained.
- **Checkpoint**: a saved set of weights.
:::
