---
id: l42
title: "Lab 9: see a scaling law in miniature"
quiz: quiz-05.yaml
resources: [../resources/minigpt.py, ../resources/lab-corpus.py, ../resources/lab09-scaling.py]
sources: [2, 8]
---
After this lab you will have trained three sizes of mini-GPT for the same number of steps and seen larger models reach lower loss.

## Shortcut: the ready-made scripts

Use the same folder as lab 8 (`minigpt.py`, `input.txt`), and add `lab09-scaling.py` from this lesson's Resources:

```bash
python lab09-scaling.py        # about 1 to 2 minutes on a laptop CPU
```

It was run while writing this course.

## What the script does

It trains three mini-GPTs that differ only in vector size (`n_embd` of 16, 32 and 64) for 600 steps each, on the same data and with the same random seed, then prints parameters against held-out loss. That is a tiny version of the experiment in the scaling-law paper, which measured loss against model size, data and compute. [2]

## What to look for

In the test run:

| Parameters | Held-out loss |
| --- | --- |
| 9,761 | 2.431 |
| 31,745 | 2.253 |
| 112,577 | 2.025 |

Each model is about three to four times larger than the one before and each has lower loss. That is the shape of the scaling-law result: more parameters, lower loss, with the same data. [2]

## What this does not show

Be careful with a three-point experiment.

- **Three points is not a law.** The paper's trend spans more than seven orders of magnitude. [2] Here the range is about one.
- **Steps were fixed at 600.** The biggest model had not finished learning. With more steps all three would improve, so the gaps would change.
- **Data was constant.** The Chinchilla paper's point is that as models grow, data should grow with them, not stay fixed (lesson 40). [8] Try training the largest model for 3000 steps and see whether it keeps improving, and when overfitting begins (lesson 19).

## Try this

- Increase `STEPS` to 1500. Does the ranking of the three models change?
- Add a fourth, larger size (`n_embd=128`). Does the trend continue? How long does it take?
- Plot parameters against loss on a log-log chart, and see whether the points lie near a line.

## Check yourself

- Which of the three axes of the scaling-law paper (model size, data, compute) did this lab vary? Which did it hold fixed?
- Why would you not draw conclusions about billion-parameter models from this lab alone?

:::key-takeaways
- In the lab, loss fell from 2.431 to 2.253 to 2.025 as parameters grew from 9,761 to 31,745 to 112,577. [2]
- Three points show the direction of a scaling law, not its shape.
:::

:::glossary
- **`n_embd`**: the size of each token's vector in the lab's model.
- **Seed**: a number that makes random choices repeatable.
- **Log-log chart**: a chart where both axes use logarithmic scales; power laws look like straight lines.
- **Ablation / controlled comparison**: changing one thing and holding the rest fixed.
- **Fixed budget**: the same number of training steps for each model.
:::
