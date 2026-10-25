---
id: l22
title: "Lab 5: build a BPE tokenizer"
quiz: quiz-03.yaml
resources: [../resources/lab05-bpe.py]
sources: [6]
---
After this lab you will have built a working byte-pair tokenizer in about 40 lines and watched a vocabulary form.

## Shortcut: the ready-made script

Download `lab05-bpe.py` from this lesson's Resources. It uses only Python's standard library:

```bash
python lab05-bpe.py
```

It was run while writing this course.

## What the script does

It follows the algorithm from lesson 21. [6] It starts from the characters of the text `low lower lowest newer newest wider widest low low newer newer`, counts adjacent pairs with `collections.Counter`, merges the most frequent pair, and repeats ten times or until no pair occurs twice.

## What to look for

In the test run the text started as 62 tokens, and the first merges were:

```
merge  1: 'w' + 'e' -> 'we'   (6x)  now 56 tokens
merge  2: 'l' + 'o' -> 'lo'   (5x)  now 51 tokens
merge  3: ' ' + 'lo' -> ' lo'   (4x)  now 47 tokens
merge  4: 'we' + 'r' -> 'wer'   (4x)  now 43 tokens
```

and after ten merges there were 25 tokens. Then the script encodes new text with the learned rules: `lowest newest` became `['lo', 'west', ' ne', 'west']`, and the unseen word `slowly` became `['s', 'lo', 'w', 'l', 'y']`, falling back to smaller pieces exactly as lesson 21 predicted. Note that `w` + ` lo` also appeared as a merge: the lab merges across spaces, which real tokenizers avoid.

## Try this

- Change `NUM_MERGES` to 3, then 30. What happens to the token count and to the vocabulary?
- Replace `TEXT` with a paragraph from a document you know. Which pieces become single tokens first?
- Make the script split on spaces first so merges never cross a word boundary. (That is one of the changes real tokenizers make.)

## Check yourself

- Why does the first merge pick `w` + `e` and not `l` + `o`?
- After more merges the text gets shorter. What is the cost of a bigger vocabulary?

:::key-takeaways
- BPE is a short loop: count pairs, merge the most frequent, repeat. [6]
- A learned tokenizer shortens text and still handles words it never saw.
:::

:::glossary
- **`collections.Counter`**: a Python tool that counts how many times each item appears.
- **Merge**: replacing two adjacent tokens with one new token.
- **Encode**: turn text into tokens using the learned rules.
- **Vocabulary**: the set of tokens after the merges, plus the original characters.
- **Word boundary**: the edge between one word and the next, such as a space.
:::
