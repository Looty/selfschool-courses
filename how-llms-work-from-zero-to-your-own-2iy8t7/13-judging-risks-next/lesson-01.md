---
id: l57
title: Judging a model honestly
quiz: quiz-01.yaml
resources: []
sources: [36, 37, 3, 8, 56]
---
After this lesson you can read a benchmark result critically, name the dimensions a fair evaluation covers, and design a small evaluation of your own.

## One score is never the story

Benchmarks compress a model into a number. Useful, but each number answers a narrow question. Three examples from this course:

- **MMLU** (multiple-choice questions across 57 subjects, from elementary mathematics and US history to computer science and law): when it was published in 2020 most models scored near random chance and the largest GPT-3 improved on chance by almost 20 percentage points on average. The authors also found performance very uneven across subjects, near chance on socially important ones such as morality and law, and that models often do not know when they are wrong. [56] Two years later Chinchilla reached 67.5% average accuracy, over 7 points above Gopher. [8]
- **TruthfulQA** (817 questions designed to trigger common misconceptions): the best model tested was truthful on 58% of questions, against 94% for humans. [37]
- **GSM8K** (math word problems): chain-of-thought prompting set a state-of-the-art accuracy in 2022 (lesson 49).

Accuracy on a benchmark does not tell you about toxicity, speed, cost, fairness, or whether the model behaves when the questions look different from the test.

## HELM: evaluate on many dimensions

The Holistic Evaluation of Language Models (HELM, Stanford, November 2022) was designed to address this. It evaluated 30 prominent models on 42 scenarios using seven metrics: accuracy, calibration, robustness, fairness, bias, toxicity and efficiency. The authors report that before HELM, models had been evaluated on an average of 17.9% of the core scenarios, and HELM raised this to 96.0%, so all 30 models were benchmarked on the same core scenarios and metrics. [36] The idea to take away is the shape: many scenarios, many metrics, same conditions for every model.

## Traps

- **Contamination.** If benchmark questions appear in the training text, scores are inflated. The GPT-3 paper itself raises methodological concerns about web-scale training data and some datasets. [3]
- **Prompt sensitivity.** Small changes in the prompt change scores, so compare models with the same prompt.
- **Averages hide failures.** A model can average well and fail badly on one group of inputs.
- **Optimising the benchmark.** When a number becomes the goal, models and training sets drift towards it.

## Your own evaluation

For an application you care about, build a small test set:

1. Collect 30 to 100 real inputs, including awkward ones.
2. Write the answer you want for each, or a rubric for judging it.
3. Run each candidate model and prompt with identical settings.
4. Score the results, ideally with a person checking a sample.
5. Re-run the set whenever you change the model, prompt or data.

A set of 50 questions that matches your use beats a famous benchmark that does not.

:::key-takeaways
- A benchmark score answers a narrow question; MMLU, TruthfulQA and GSM8K measure different things. [8][37]
- HELM evaluated 30 models on 42 scenarios with 7 metrics, under the same conditions. [36]
- Beware contamination, prompt sensitivity and averages that hide failures. [3]
- Build a small test set that matches your own use.
:::

:::glossary
- **Benchmark**: a fixed set of test questions used to compare models.
- **MMLU**: a benchmark of multiple-choice questions across many subjects.
- **TruthfulQA**: a benchmark of questions that tempt models into false answers.
- **HELM**: Stanford's holistic evaluation across many scenarios and metrics.
- **Calibration**: whether a model's confidence matches how often it is right.
- **Robustness**: staying accurate when inputs are changed slightly.
- **Contamination**: test data leaking into training data.
- **Rubric**: a written guide for scoring an answer.
:::
