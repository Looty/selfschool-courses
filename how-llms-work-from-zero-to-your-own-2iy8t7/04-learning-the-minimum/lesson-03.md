---
id: l17
title: "Lab 4: gradient descent from scratch"
quiz: quiz-03.yaml
resources: [../resources/lab04-gradient-descent.py]
sources: [32]
---
After this lab you will have trained a straight-line model by gradient descent in about 25 lines, and seen a good, a slow and an exploding learning rate.

## Shortcut: the ready-made script

Download `lab04-gradient-descent.py` from this lesson's Resources. It needs only numpy:

```bash
uv venv && uv pip install numpy
python lab04-gradient-descent.py        # learning rate 0.01
python lab04-gradient-descent.py 0.3
python lab04-gradient-descent.py 1.2
```

It was run while writing this course.

## What the script does

It makes 50 noisy points on the line y = 3x + 2, starts the model at w = 0, b = 0, and applies the four steps from lesson 16 a thousand times: compute the MSE loss, compute the two gradients (the formulas from the crash course), and update. [32] It prints the loss and the parameters at steps 1, 10, 100 and 1000.

## What to look for

In test runs, the first step always had loss 13.645, because the starting model predicts 0 for everything.

| Learning rate | After 1000 steps | Verdict |
| --- | --- | --- |
| 0.01 | w = 2.66, b = 2.20, loss 0.0235 | Still converging: too slow |
| 0.3 | w = 3.05, b = 1.98, loss 0.0099 | Good: reached the noise floor |
| 1.2 | loss 9,466,592 at step 10 and growing | Blew up: steps overshoot more each time |

The "truth" is w = 3, b = 2, and the data has noise, so you cannot expect exactly 3 and 2. With rate 0.3 the answer is close; with 0.01 it had not got there yet, which is why people tune the learning rate.

## Check yourself

- Why is the loss at step 1 the same for every learning rate?
- With rate 1.2 the loss grows each step. Explain in terms of "overshooting the bottom of the bowl".
- Change the data to y = −5x + 10. Do the same learning rates still work?

:::key-takeaways
- Gradient descent fits a line in a few lines of code. [32]
- The same starting loss with different learning rates shows the effect of step size: slow, good, or exploding.
:::

:::glossary
- **numpy**: Python's standard library for fast arithmetic on arrays of numbers.
- **Noise**: random variation in data that no model should try to fit exactly.
- **Noise floor**: the lowest loss reachable when the data itself is noisy.
- **Hyperparameter**: a setting you choose before training, such as the learning rate.
- **Tune**: try different hyperparameter values to find one that works well.
- **Diverge**: the loss growing instead of shrinking.
:::
