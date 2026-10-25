---
id: l44
title: "RLHF: learning from human preferences (InstructGPT, 2022)"
quiz: quiz-02.yaml
resources: []
sources: [4, 21, 48, 49]
---
After this lesson you can explain the three steps of reinforcement learning from human feedback, and why preference rankings are used instead of ideal answers.

## Why not just write more ideal answers?

Writing a great answer is expensive. *Ranking* answers is easier and faster: show a person four answers to the same prompt and ask which is best. Reinforcement learning from human feedback (RLHF) uses that cheaper signal.

## The three steps

The InstructGPT paper (Ouyang et al., March 2022) describes the approach. [4]

1. **Supervised fine-tuning.** Labelers write demonstrations of the desired behaviour, and GPT-3 is fine-tuned on them (lesson 43). [4]
2. **Reward model.** Collect rankings of several model outputs for the same prompt. Wikipedia describes the next stage as learning a **reward model** that learns which responses people prefer. [21][4] The reward model reads a prompt and a response and outputs a score that tries to predict the human ranking.
3. **Reinforcement learning.** Then the language model is tuned with reinforcement learning to produce responses that score highly on the reward model. [21][4] Reinforcement learning is training by trial and reward: generate a response, get a score, adjust to make high-scoring responses likelier.

## The people and the data

The paper is specific about who did the work. OpenAI hired a team of 40 contractors, chosen by their performance on a screening test, to label data. They wrote demonstrations of desired behaviour on (mostly English) prompts submitted to the OpenAI API plus some labeler-written prompts, and later ranked comparisons between model outputs. The authors say this procedure "aligns the behavior of GPT-3 to the stated preferences of a specific group of people", mainly the labelers and the researchers who wrote their instructions, not to any broader notion of human values. [4]

## Where PPO and the idea of human preferences come from

The reinforcement-learning step uses PPO, Proximal Policy Optimization (Schulman et al., 2017): a family of policy-gradient methods that alternate between collecting data from interaction and optimising a "surrogate" objective, allowing several epochs of minibatch updates per batch, and keeping some benefits of trust-region methods while being simpler to implement. [48] And learning from human *comparisons* was shown earlier, in games and robot simulations: Christiano et al. (2017) defined goals through non-expert humans' preferences between pairs of trajectory segments, with feedback on less than 1% of the agent's interactions, and trained novel behaviours with about an hour of human time. [49]

## The "alignment tax" and how it was reduced

RLHF has a cost. InstructGPT's authors found their procedure made performance worse on some public NLP benchmarks, which they call an "alignment tax": the alignment procedure comes at the cost of lower performance on certain tasks you may care about. They greatly reduced these regressions by mixing the PPO updates with updates that increase the log-likelihood of the pretraining distribution, a variant they call **PPO-ptx**, without lowering the labelers' preference scores. [4] They also tested "held-out" labelers who had produced none of the training data, and found they preferred InstructGPT outputs over GPT-3 at about the same rate, though they call this preliminary. [4]

## The result

In human evaluations on the authors' prompts, the 1.3-billion-parameter InstructGPT model was preferred over the 175-billion-parameter GPT-3, despite having about 100 times fewer parameters. InstructGPT also showed gains in truthfulness and reductions in toxic output, with minimal regressions on public NLP datasets. The authors conclude that fine-tuning with human feedback is a promising direction for aligning models with human intent, while noting that InstructGPT still makes simple mistakes. [4]

This is the technique that turned GPT-3 into the assistant behind ChatGPT, which launched in late 2022. [21]

## Costs and risks to keep in mind

- **Whose preferences?** The reward model encodes the views of the labelers and the instructions they were given.
- **Reward hacking.** A model optimised against a learned score can find answers that score well without being good. This is a general risk of optimising any proxy measure; the sources read here do not analyse it for RLHF.
- **Complexity.** The pipeline has several moving parts (a reward model, an RL loop), which is the motivation for the simpler method in the next lesson.

:::key-takeaways
- RLHF: supervised fine-tuning, then a reward model trained on human rankings, then reinforcement learning against it. [4][21]
- A 1.3B InstructGPT was preferred over the 175B GPT-3 by human raters. [4]
- Rankings are cheaper to collect than ideal answers, but the reward model carries the labelers' judgments: 40 contractors in InstructGPT. [4]
- RLHF has an "alignment tax" on some benchmarks, reduced by PPO-ptx (mixing in pretraining updates). [4]
:::

:::glossary
- **RLHF**: reinforcement learning from human feedback.
- **Reward model**: a model trained to score responses the way humans would rank them.
- **Reinforcement learning (RL)**: training by trying actions and adjusting toward those that earn higher reward.
- **Ranking**: ordering several responses from best to worst.
- **Reward hacking**: scoring well on the learned reward without actually being good.
- **InstructGPT**: OpenAI's 2022 model trained with this recipe.
- **Regression (on benchmarks)**: getting worse at a measured task.
:::
