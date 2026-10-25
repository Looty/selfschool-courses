---
id: l46
title: Success criteria for LLM applications
quiz: quiz-02.yaml
resources: []
sources: [62]
---
After this lesson you can write success criteria for an LLM application that are specific, measurable, achievable and relevant, and combine several into one release bar.

## Why criteria come first

An LLM application is built on a large language model that you steer mainly with a prompt (the written instructions you give it). Anthropic's documentation frames evaluation as a cycle: define success criteria (what "good enough" means), build evaluations ("evals", repeatable tests) that measure against them, then improve the prompt and repeat. [62] You cannot tell whether a prompt change helped unless you wrote down what "better" means. This is the same idea as the baseline and metric choices of lessons 5 and 7, with a harder measurement problem.

## Four properties of a good criterion

The page says good criteria are: [62]

- **Specific.** "Accurate sentiment classification", not "good performance".
- **Measurable.** Use quantitative metrics or well-defined qualitative scales. Qualitative measures are useful when applied consistently alongside quantitative ones. Even safety can be quantified, for example "less than 0.1% of outputs out of 10,000 trials flagged for toxicity".
- **Achievable.** Base targets on benchmarks, prior experiments, research or expert knowledge, and keep them realistic for current frontier models.
- **Relevant.** Align with the application's purpose. Citation accuracy matters more for a medical application than for a casual chatbot.

## Common criteria

The page lists: task fidelity, consistency, relevance and coherence, tone and style, privacy preservation, context utilisation, latency and price. Most use cases need several evaluated together. [62]

Its multi-criteria example for a sentiment classifier: an F1 score of at least 0.85, 99.5% of outputs non-toxic, and 95% of responses in under 200 ms. [62] Three criteria, three kinds of measure (quality, safety, latency), one release bar.

## From criteria to a gate

Connect this to the release gate of lesson 16. A model-release gate compares candidate against baseline on a metric; an LLM release gate can hold several thresholds at once. Write them as a table before building anything.

| Criterion | Measure | Threshold | Source of the threshold |
| --- | --- | --- | --- |
| Task fidelity | F1 on a labelled test set | at least 0.85 | Prior experiment or benchmark |
| Safety | Share of outputs flagged | below 0.1% over 10,000 trials | Policy |
| Latency | Share of responses under 200 ms | at least 95% | User need |

The values come from the page's examples and are placeholders; the "source of the threshold" column is the course's addition, because the page's "achievable" rule only works if you know where a target came from. [62]

## Pitfalls

- **Vague criteria** such as "helpful answers" cannot be scored; split them into measurable parts or define a rubric (lesson 47).
- **One criterion only.** An application can win on accuracy and lose on latency or price; the page says most need several.
- **Targets that ignore the task.** Edge cases and the distribution of real inputs matter; the next lesson returns to this.

:::low-confidence
The page is a vendor's documentation for its own models. The principles are general, but the specific numbers (0.85 F1, 99.5%, 200 ms) are illustrative. Part of the page was not read. [62]
:::

:::key-takeaways
- Define success criteria before building evals: specific, measurable, achievable, relevant. [62]
- Most applications need several criteria, such as quality, safety, latency and price. [62]
- Write the criteria as a threshold table and make it the release gate. [62]
:::

:::glossary
- **LLM (large language model)**: a model trained on huge amounts of text that can write, summarise and answer.
- **Prompt**: the instructions and context you give the model.
- **Eval (evaluation)**: a repeatable test that scores an application's outputs.
- **Success criteria**: the written definition of "good enough".
- **Specific / measurable / achievable / relevant**: the four checks for a good criterion.
- **Benchmark**: a standard test used to compare systems.
- **Frontier model**: one of the most capable models currently available.
- **Toxicity**: harmful, abusive or offensive content.
- **Task fidelity**: how faithfully the output does the job asked.
- **Consistency**: similar inputs give similar outputs.
- **Context utilisation**: how well the model uses the information provided to it.
- **F1 score**: one number (0 to 1) combining precision and recall; higher is better.
- **ms (millisecond)**: a thousandth of a second.
- **Release bar / gate**: the thresholds that must all be met before shipping.
- **Rubric**: a written scoring guide.
- **Sentiment classification**: deciding whether text is positive, negative or neutral.
:::
