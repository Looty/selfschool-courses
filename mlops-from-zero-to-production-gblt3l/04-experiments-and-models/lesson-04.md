---
id: l16
title: Validating a model before it ships
quiz: quiz-04.yaml
resources: []
sources: [1, 3, 13]
---
After this lesson you can list the offline and online checks a model should pass before it serves traffic, and decide which should block a release automatically.

## Validation is a gate

In the lifecycle, validation is the step that decides whether a model is adequate for deployment. [1] The Level 1 pipeline automates it as a gate between training and serving, and Level 2 keeps it in the delivery stages. A model that fails does not reach the registry's production alias.

## Offline validation

Google's guide lists the offline checks. [1]

- Evaluate the model's metrics on a test dataset to assess its predictive quality.
- Compare the new model's metrics with the current production model and with a baseline.
- Check that performance is consistent across segments of the data. An average can hide a segment where the model fails.
- Test the model for infrastructure compatibility and API consistency: the packages it needs, memory, compute and accelerators, and that the prediction service accepts the expected inputs and returns the expected outputs.

Rule #9 of the Rules of Machine Learning adds a mindset: detect problems before exporting models by running sanity checks, such as performance on held-out data. The guide's suggestion is to treat trouble with a model that has not shipped as a lower-urgency alert, and trouble with a user-facing model as something that may justify a page. [13]

## Online validation

Passing offline checks does not prove the model works on live traffic. The guide's online validation is a **canary deployment** (send the new model a small slice of real traffic first, like a canary in a coal mine) or an **A/B test** (run two versions side by side and compare) before the model serves everyone. [1] Lesson 23 covers release strategies. For this lesson, note the order: offline checks decide whether the model may be tried, and live evidence decides whether it replaces the current one.

## How many tests?

Testing ML is a larger topic than any single list. The "ML Test Score" paper, written from experience with production ML systems, offers 28 specific tests and monitoring needs as a roadmap for production readiness and for paying down technical debt. The authors point out that specifying a model's expected prediction behaviour in advance is hard, which is one reason concrete tests are difficult to write. [3]

:::low-confidence
Only the abstract of the ML Test Score paper could be read; its PDF would not parse. This course therefore states the count (28) and the purpose but does not list the individual tests or the scoring method. Read the paper before quoting more. [3]
:::

## A practical gate

A minimal automated gate that follows the sources: [1]

1. Metrics on a held-out test set beat the baseline and are not worse than the production model.
2. Per-segment metrics are within the tolerance you decided in advance.
3. The package loads in the target environment and returns the expected output shape for a known input.
4. Only then is the version made eligible for a canary.

Write the thresholds down. A gate that depends on someone's judgement every time will not run in a pipeline.

:::key-takeaways
- Validation decides whether a model is adequate to deploy; it is a gate, not a report. [1]
- Offline: metrics against baseline and current model, per-segment consistency, infrastructure and API compatibility. [1]
- Online: canary or A/B before serving everyone. [1]
- Sanity-check before exporting models (Rule #9). [13]
:::

:::glossary
- **Gate**: an automatic check that must pass before something moves on.
- **Offline validation**: testing on saved data, before real users are involved.
- **Online validation**: testing on live traffic.
- **Baseline**: the simple reference model or rule to beat.
- **Segment**: a subgroup of the data, such as one region.
- **Infrastructure compatibility**: the model can actually run on the target machines (memory, accelerators, libraries).
- **Accelerator**: special hardware (like a GPU) that speeds up model maths.
- **Sanity check**: a quick test that catches obviously broken results.
- **Held-out data**: data not used for training.
- **Canary deployment**: releasing to a tiny share of users first.
- **A/B test**: comparing two versions on live traffic.
- **Technical debt**: shortcuts that make later work harder.
- **ML Test Score**: a paper's checklist of 28 tests for production-ready ML.
- **Tolerance**: the amount of difference you accept.
- **Page (someone)**: wake the on-call person with an alert.
:::
