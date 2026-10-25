---
id: l65
title: "Constitutional AI: feedback from an AI, guided by written principles"
quiz: quiz-06.yaml
resources: []
sources: [50, 4, 14]
---
After this lesson you can explain how Constitutional AI replaces human harm labels with written principles, and where it sits next to RLHF and DPO.

## The problem it tackles

RLHF (lesson 44) needs people to label which outputs are better, including which are harmful. That is slow and costly, and it exposes labelers to disturbing text. Constitutional AI (Bai et al., Anthropic, December 2022) asks whether the labelling can be largely done by the model itself, with human oversight supplied only through a short list of written principles, "a constitution". [50]

## The two phases

The abstract describes the method. [50]

1. **Supervised phase (critique and revision).** Sample responses from an initial model, including to harmful prompts. Have the model *critique* its own response against a principle and then *revise* it. Fine-tune the original model on the revised responses.
2. **Reinforcement-learning phase (RLAIF).** Sample pairs of responses from the fine-tuned model and ask an AI model, guided by the principles, which of the two is better. These AI judgements train a **preference model**, which then serves as the reward signal for reinforcement learning. The authors call this **reinforcement learning from AI feedback (RLAIF)**.

The structure is RLHF's (lesson 44) with the human comparison replaced by an AI comparison under the principles.

## What the authors report

The resulting assistant is "harmless but non-evasive": when faced with harmful requests it engages with them by explaining its objections rather than refusing flatly. Chain-of-thought-style reasoning (lesson 49) used by the AI judge can improve both the human-judged performance and the transparency of its decisions. The approach, they say, makes it possible to control AI behaviour more precisely with far fewer human labels. [50]

## How to place it

| Method | Where the preference signal comes from | Training |
| --- | --- | --- |
| RLHF | Human rankings of outputs [4] | Reward model, then PPO |
| DPO | Human preference pairs [14] | Direct loss on pairs, no reward model |
| Constitutional AI (RLAIF) | An AI judge following written principles [50] | Preference model from AI labels, then RL |

They are not rivals so much as options for where preference data comes from and how it is used. A model's behaviour reflects whoever wrote the demonstrations, the rankings or the constitution; the InstructGPT authors say plainly that their procedure aligns GPT-3 to the preferences of a specific group of people. [4] A constitution makes those values explicit and editable, but someone still chose them.

:::low-confidence
Only the abstract of the Constitutional AI paper was read. The principles it used, the size of its datasets and its results tables are not covered here. [50]
:::

:::key-takeaways
- Constitutional AI uses written principles instead of human harm labels: a critique-and-revise supervised phase, then RL from AI feedback. [50]
- The result is meant to be harmless but not evasive, with far fewer human labels. [50]
- RLHF, DPO and RLAIF differ in where preference data comes from and how it is used. [4][14][50]
:::

:::glossary
- **Constitution (here)**: a short list of written principles used to guide the AI's judgements.
- **Critique and revision**: the model criticises its own response against a principle, then rewrites it.
- **RLAIF**: reinforcement learning from AI feedback.
- **Preference model**: a model that scores which of two responses is better.
- **Harmless but non-evasive**: declining harmful requests while explaining why, instead of a flat refusal.
- **Oversight**: how humans guide and check a system's behaviour.
:::
