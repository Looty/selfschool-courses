---
id: l45
title: "DPO: a simpler route to preferences (2023)"
quiz: quiz-03.yaml
resources: []
sources: [14, 4]
---
After this lesson you can say what Direct Preference Optimization changes about RLHF, and why people adopted it.

## What was awkward about RLHF

RLHF (lesson 44) is a pipeline of separate parts. You fit a reward model, then use reinforcement learning to optimise the language model against it. The DPO paper describes this as complex and often unstable. [14] Reinforcement learning needs sampling from the model during training and careful tuning.

## The DPO idea

In May 2023 Rafailov and colleagues (Stanford) published "Direct Preference Optimization: Your Language Model is Secretly a Reward Model". [14] Their observation: by re-expressing the reward model in terms of the language model itself, the best policy can be written in closed form. The whole RLHF problem then reduces to "a simple classification loss" on pairs of preferred and rejected responses. [14]

In plain terms, instead of the three-stage pipeline you train directly on pairs: for a prompt, a response people preferred and one they rejected. The loss pushes the model to raise the probability of the preferred response relative to the rejected one, while a frozen copy of the starting model (the reference) keeps it from drifting too far.

## Why it spread

The authors report that DPO avoids sampling from the model during fine-tuning, needs little hyperparameter tuning, controls generation sentiment better than PPO-based RLHF in their experiments, and matches or improves response quality on summarisation and single-turn dialogue, while being simpler to implement and train. [14]

:::low-confidence
Only the abstract was read. Which approach works best depends on the task and scale, and later work compares them further; this lesson reports the paper's own claims. [14]
:::

## The same data

Both methods start from the same kind of data: human judgments of which response is better. What changes is how the judgments become a trained model: through an explicit reward model and RL, or through a direct loss on pairs. [4][14] In the next lab you will run the DPO loss on a toy problem.

:::key-takeaways
- RLHF fits a reward model and then uses RL, which is complex and often unstable. [14]
- DPO reduces the problem to a simple classification-style loss on preferred/rejected pairs. [14]
- Both use human preference data; DPO skips the explicit reward model and the RL loop. [14]
:::

:::glossary
- **DPO (Direct Preference Optimization)**: training directly on preferred/rejected response pairs with a simple loss.
- **Policy**: the model's way of choosing outputs; here, the language model itself.
- **Reference model**: a frozen copy of the starting model that DPO compares against.
- **Closed form**: an exact formula, with no iterative search needed.
- **PPO**: a reinforcement-learning algorithm commonly used in RLHF.
- **Preference pair**: a prompt with one preferred and one rejected response.
:::
