---
id: l46
title: "Lab 10: preference tuning in miniature"
quiz: quiz-04.yaml
resources: [../resources/lab10-preference-demo.py]
sources: [14]
---
After this lab you will have run the DPO loss on a toy problem and watched preferences turn into probabilities.

This lab is a **teaching demo, not a language model**. The "policy" chooses between four canned replies instead of generating text, so that the effect of the loss is visible in four numbers.

## Shortcut: the ready-made script

Download `lab10-preference-demo.py` from this lesson's Resources:

```bash
uv venv && uv pip install torch
python lab10-preference-demo.py
```

It was run while writing this course.

## What the script does

- Four candidate replies: "I don't know.", "Here is a clear, correct answer.", "Here is a rude answer.", "Here is a long, rambling answer."
- Five human judgments as (preferred, rejected) pairs: clear beats unhelpful, rude and rambling; rambling beats rude; "I don't know" beats rude.
- The policy starts with equal scores. A frozen copy is the reference.
- For each pair it computes the DPO loss: it measures how much more the policy likes the preferred reply than the reference does, minus the same for the rejected reply, scaled by `beta`, and applies a log-sigmoid. Minimising it raises the preferred reply and lowers the rejected one. [14]

## What to look for

In the test run, the probabilities moved like this:

| Step | clear | "don't know" | rambling | rude |
| --- | --- | --- | --- | --- |
| 0 | 0.28 | 0.25 | 0.25 | 0.23 |
| 50 | 0.96 | 0.02 | 0.02 | 0.00 |
| 200 | 1.00 | 0.00 | 0.00 | 0.00 |

The loss fell from 0.693 (the value for a coin toss) to 0.020. The policy ends up saying the clear answer almost always, because it won every comparison it was in.

## What this toy hides

- Real preference data is noisy and sometimes contradictory; this data is perfectly consistent.
- Real policies produce free text from billions of parameters; here there are four numbers.
- The model collapsed to a single reply. In real training `beta` and the reference model keep the model close to its starting behaviour (lesson 45), but a toy with no other pressure drifts to the extreme.

## Try this

- Add the pair (2, 1) (rude preferred over clear). The data now contradicts itself. What does the policy do?
- Lower `beta` to 0.1 and raise it to 2.0. How does the speed of change differ?

:::key-takeaways
- The DPO loss turns pairs of preferred/rejected choices into a push on probabilities. [14]
- With consistent preferences the toy policy puts almost all probability on the winner.
:::

:::glossary
- **Policy**: here, a set of probabilities over four replies.
- **Preferred / rejected**: the reply people liked better / worse in a comparison.
- **`beta`**: a setting for how strongly to stay near the reference.
- **Log-sigmoid**: the smooth function used to turn a margin into a loss.
- **Margin**: how much more the policy favours the preferred reply than the rejected one, relative to the reference.
- **Collapse**: the policy putting nearly all probability on one option.
:::
