---
id: l63
title: "Emergent abilities: real, or a mirage?"
quiz: quiz-06.yaml
resources: []
sources: [54, 55, 12]
---
After this lesson you can state the emergent-abilities claim, the "mirage" counter-argument, and why the choice of metric matters when you read a scaling result.

## A striking claim

Lesson 39 said loss falls smoothly and predictably with scale. But people also noticed that some *skills*, such as multi-digit arithmetic or following a chain of reasoning (lesson 49), seemed absent in small models and then present in large ones. Wei and colleagues' 2022 paper "Emergent Abilities of Large Language Models" gave it a definition: an ability is emergent "if it is not present in smaller models but is present in larger models". Scaling is known to improve performance predictably on many tasks; emergent abilities are the opposite case, appearing unpredictably as models grow, which means they cannot be forecast by extrapolating the performance of smaller models. If emergence is real, the authors note, further scaling could expand what language models can do. [54] The chain-of-thought result (lesson 49) is one example: the prompting method helped only in sufficiently large models. [12]

## The counter-argument

In April 2023 Schaeffer, Miranda and Koyejo asked: "Are Emergent Abilities of Large Language Models a Mirage?" Their abstract argues that apparent emergent abilities may come from the researcher's choice of metric, not from a fundamental change in model behaviour with scale. [55]

The idea is simple. Take a task graded all-or-nothing, such as "is the 5-digit sum exactly right?" A model that gets each digit right 90% of the time gets all five right only about 59% of the time (0.9⁵), and one with 60% per-digit accuracy gets about 8%. Per-digit accuracy may rise smoothly with scale, but the exact-match score looks flat near zero for a long stretch and then shoots up. (The numbers in this example are an illustration of the arithmetic, not results from the paper.) The paper says that nonlinear or discontinuous metrics produce apparent emergent abilities, while linear or continuous metrics show smooth, predictable improvement. They support the claim with three analyses: testing metric-choice predictions on the InstructGPT/GPT-3 model family, a meta-analysis of BIG-Bench tasks, and showing that metric choice can create seemingly emergent abilities in vision tasks across deep networks. They conclude that alleged emergent abilities may "evaporate with different metrics or with better statistics" and may not be a fundamental property of scaling. [55]

## How to hold both ideas

- The *score* on a task can really jump with scale; that is what users experience.
- Whether the *underlying ability* jumped, or only the metric made a smooth change look like a jump, is the dispute. These two papers do not settle it; the mirage paper shows that the evidence for sudden jumps depends on the metric. [54][55]
- For planning, the practical lesson is the same as lesson 57: always ask what is being measured and how, before you conclude that a model "can" or "cannot" do something.

## A concrete habit

When someone says "model X can't do Y but model Z can", ask for a *continuous* measure (partial credit, per-step accuracy, log-probability of the right answer) as well as the pass/fail one. If the continuous measure also jumps, the effect is more likely real.

:::key-takeaways
- Emergent ability (Wei et al. 2022): present in larger models but not in smaller ones, so not predictable by extrapolation. [54]
- Counter-argument (Schaeffer et al. 2023): nonlinear or discontinuous metrics create apparent emergence; continuous metrics show smooth improvement. [55]
- Always check the metric before concluding a model has or lacks a skill.
:::

:::glossary
- **Emergent ability**: a skill present in larger models but not in smaller ones.
- **Extrapolate**: predict beyond the range you measured by extending a trend.
- **Metric**: the number used to score a model on a task.
- **Discontinuous / nonlinear metric**: one that jumps (such as exact match: right or wrong), rather than moving smoothly.
- **Continuous metric**: one that changes smoothly with partial credit.
- **Exact match**: counts an answer as right only if it matches the target exactly.
- **BIG-Bench**: a large collection of diverse tasks for testing language models.
- **Meta-analysis**: combining results across many studies or tasks.
:::
