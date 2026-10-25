---
id: l27
title: "Lab 6: a bigram model from scratch"
quiz: quiz-04.yaml
resources: [../resources/lab-corpus.py, ../resources/lab06-bigram.py]
sources: [17, 30]
---
After this lab you will have built a counting language model in about 40 lines, sampled from it at different temperatures, and measured its loss on text it had not seen.

## Shortcut: the ready-made scripts

Download `lab-corpus.py` and `lab06-bigram.py` from this lesson's Resources. They use only Python's standard library:

```bash
python lab-corpus.py        # creates input.txt (about 1 MB of Shakespeare)
python lab06-bigram.py
```

`lab-corpus.py` downloads the Shakespeare file the nanoGPT README uses; if the download fails it writes a small made-up text instead, so everything still runs. [17] Both scripts were run while writing this course.

## What the script does

1. Reads `input.txt`; the first 90% is for training and the last 10% is held out.
2. Counts, for each character, which characters follow it.
3. Turns counts into probabilities with +1 smoothing (lesson 24).
4. Samples 300 characters, using a temperature (lesson 25). [30]
5. Measures the loss on held-out text (lesson 26).

## What to look for

In the test run:

- There were 65 distinct characters. After `t` the most common successor was `h` (20,592 times), then space (14,879).
- The sampled text had English-looking fragments ("Whe irtthogor s.", "BRomanthend p") but no sense.
- The loss on held-out text was **2.493 nats per character** (perplexity 12.1), against **4.174** for guessing uniformly.

## Try this

- Set `TEMPERATURE` to 0.5, then 2.0 and run again. Which output looks most like English? Which is closest to random letters?
- The script uses one character of context. Change it to use the previous *two* characters (a trigram). Does the loss fall? What happens to the size of the count table?
- Print the 10 most likely successors of a space. Do they match your intuition about what starts an English word?

## Check yourself

- Why does the count table for two characters of context have 65 times more rows? (Hint: Shannon, lesson 7.)
- The bigram text never forms a real sentence. What would a model need to do that this one cannot?

:::key-takeaways
- A counting model plus smoothing is a complete, working language model. [17]
- Loss on held-out text (2.493) beats uniform guessing (4.174) but the output still lacks meaning.
- The mini-GPT in chapter 8 plays the same game with much more context.
:::

:::glossary
- **`input.txt`**: the practice text file the labs read.
- **Held-out split**: the last part of the text, kept out of training.
- **Trigram**: using the previous two characters as context.
- **Count table size**: the number of rows grows by the vocabulary size for each extra character of context.
- **Download fallback**: a built-in small text used when the real file cannot be downloaded.
:::
