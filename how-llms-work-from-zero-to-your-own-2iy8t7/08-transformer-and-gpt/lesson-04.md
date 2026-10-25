---
id: l37
title: Generating text, one token at a time
quiz: quiz-04.yaml
resources: []
sources: [30, 21]
---
After this lesson you can trace the generation loop of a GPT, including the context window limit and stopping.

## The loop in code

From `minigpt.py`:

```python
def generate(self, idx, n_new, temperature=1.0):
    for _ in range(n_new):
        logits, _ = self(idx[:, -self.c.block_size:])      # 1. keep only the last 64 tokens
        probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)   # 2. scores for the last position -> probabilities
        idx = torch.cat([idx, torch.multinomial(probs, 1)], dim=1)  # 3. sample one token and append it
    return idx
```

Three things to notice.

1. **Only the last position matters.** The model computes a prediction at every position, but for generation only the final one is used: the distribution over what comes after the whole text so far.
2. **The window slides.** The model can only see its context window (lesson 2), so once the text is longer than the window, the earliest tokens are dropped. In the lab the window is 64 characters; a modern model's window is many thousands of tokens, but the rule is the same: anything outside is invisible. [21]
3. **Sampling with temperature.** Dividing the logits by the temperature before softmax is exactly lesson 25, and `multinomial` is the random draw. [30]

## How a hosted model knows when to stop

The Hugging Face documentation says a model generates the next token until it reaches a predefined length or an end-of-sequence (`EOS`) token. [30] During training the model sees a special token marking the end of documents, so it learns to emit it when a text is complete. Chat products add the user's and the assistant's turns into the same sequence and keep generating until that end marker (or a length limit) appears.

The documentation also warns about two common mistakes. The default `generate()` returns only about 20 new tokens unless you set `max_new_tokens`; and decoder-only models return the original prompt followed by the new tokens, so you may need to cut the prompt off before showing the answer. [30]

## Speed

Each new token needs a full pass through the model, and a pass cannot start until the previous token has been chosen. This is why long answers take time even on fast hardware: writing is sequential even though training was parallel. (Techniques that cache earlier computations exist but are outside the sources of this course.)

:::key-takeaways
- Generation repeats: run the model on the last tokens, sample the next, append. [30]
- The context window slides: tokens beyond it are no longer visible to the model. [21]
- Generation stops at an end-of-sequence token or a length limit; always set `max_new_tokens`. [30]
:::

:::glossary
- **Autoregressive**: generating one token at a time, feeding each output back as input.
- **Context window**: the number of most recent tokens the model can see.
- **EOS (end-of-sequence) token**: the special token that marks the end of a text.
- **`max_new_tokens`**: the cap on how many tokens to generate.
- **Multinomial sampling**: drawing one item at random according to a list of probabilities.
- **Logits**: the raw scores before softmax.
:::
