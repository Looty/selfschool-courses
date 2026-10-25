---
id: l32
title: "Lab 7: self-attention in numpy"
quiz: quiz-04.yaml
resources: [../resources/lab07-attention.py]
sources: [20]
---
After this lab you will have computed self-attention for a three-word sentence with numpy, read the attention weights, and seen the effect of the "no peeking" mask.

## Shortcut: the ready-made script

Download `lab07-attention.py` from this lesson's Resources:

```bash
uv venv && uv pip install numpy
python lab07-attention.py
```

It was run while writing this course.

## What the script does

It follows the six steps of lesson 31. [20]

1. Gives each of "the", "cat", "sat" a random 4-number embedding (stand-ins for learned ones).
2. Multiplies by three random matrices to get queries, keys and values.
3. Scores all pairs, scaled by the square root of 4.
4. Applies a **causal mask**: a word may only look at itself and earlier words, never ahead. This is what makes a GPT-style model a *next-token predictor*: when predicting the token after "cat", it must not see "sat". Masked scores are set to minus infinity so softmax gives them weight zero.
5. Applies softmax and takes the weighted sum of the values.

## What to look for

In the test run the table of weights was:

```
          the     cat     sat
     the    1.00    0.00    0.00
     cat    0.11    0.89    0.00
     sat    0.04    0.20    0.76
```

Row = the word that is looking; column = the word it looks at. The upper triangle is zero because of the mask. "the" can only see itself, so its row is 1.00 in the first column. Each row adds up to 1, and the output has the same shape as the input, one new vector per word.

The specific numbers come from random matrices, so they mean nothing here. In a trained model the same structure carries meaning: "sat" might put high weight on "cat" because that is its subject.

## Try this

- Remove the masking lines. How does the table change, and why would that be wrong for a next-token predictor?
- Change the random seed or the vector size `d`. What stays the same about the table?
- Add a fourth word. How big does the weights table become? (This is why attention cost grows with the square of the sequence length.)

## Check yourself

- Why is the first row always `1.00 0.00 0.00`?
- Which line of code makes sure each row adds up to 1?

:::key-takeaways
- Self-attention is a few matrix multiplications and a softmax. [20]
- The causal mask zeroes the weights on later tokens, so predicting the next token cannot cheat.
- The weights table is tokens × tokens, so its size grows with the square of the length.
:::

:::glossary
- **Causal mask**: a rule blocking each token from looking at later tokens.
- **Minus infinity**: a score so low that softmax turns it into weight 0.
- **Lower-triangular**: nonzero only on and below the diagonal; the shape of the allowed weights.
- **Quadratic cost**: work growing with the square of the input length.
- **Seed**: the number that starts a random generator, making results repeatable.
:::
