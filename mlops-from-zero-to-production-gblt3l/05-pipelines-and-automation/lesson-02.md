---
id: l18
title: "CI for ML: testing code, data and models"
quiz: quiz-02.yaml
resources: []
sources: [1, 3, 14, 38]
---
After this lesson you can list what continuous integration should test in an ML project and show metrics on a pull request.

## CI grows three new targets

In ordinary software, CI builds the code and runs unit and integration tests. For ML, Google's guide says CI is no longer only about testing code and components; it also tests and validates data, data schemas and models. [1] CD4ML groups the tests the same way: validating data, component integration through contract tests, model quality through threshold tests, and bias and fairness across slices of the data. [14]

## What to test

The guide lists tests that belong in continuous integration for the pipeline: [1]

- unit tests for the logic that prepares inputs (feature engineering), for example one-hot encoding (turning a category into a row of 0s and 1s), and for the methods your model uses;
- a test that **training converges**: the loss goes down, and the model can memorise a handful of sample records (if it cannot even do that, something is broken);
- a test that training does **not produce NaN values** ("not a number", the result of things like dividing by zero or mixing huge and tiny numbers);
- tests that each **component produces the expected artifacts**;
- **integration tests** between pipeline components.

Each is cheap, deterministic enough to run on every commit, and catches a class of failure that would otherwise appear in a training run hours later.

The ML Test Score paper offers 28 concrete tests and monitoring needs for production readiness, drawn from experience with production ML systems. [3] It is a good source of ideas once these basics run in CI.

:::low-confidence
Only the abstract of the ML Test Score paper was readable, so the 28 tests are not listed here. [3]
:::

## Show the numbers where people review

A change to a model's code or data should show its effect during review. CML (Continuous Machine Learning) does this in GitHub Actions: the documentation's example workflow runs on every push, trains a model, writes a report with a metrics file and a plot, and posts it to the pull request with `cml comment create report.md`. [38]

```yaml
# sketch of the documented pattern
on: [push]
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: iterative/setup-cml@v2
      - run: |
          pip install -r requirements.txt
          python train.py
          cat metrics.txt >> report.md
          cml comment create report.md
```

The setup action `iterative/setup-cml@v2` installs CML in the workflow; it provides `cml comment create` for posting results to pull requests and `cml runner` for provisioning cloud or on-premises compute for training. It does not include DVC, which needs its own setup action. [38]

:::low-confidence
The YAML above is a sketch assembled from the documented pattern, not the page's verbatim workflow. The page's example uses a CML Docker image and an image-hosting secret for plots; check the page for the exact file before copying it. [38]
:::

## What not to put in CI

Full training on production-sized data usually does not belong in a pull request check. CI should prove that the pipeline and its components work on small data. Full training belongs in the pipeline that runs on triggers (lesson 20), where its output is validated before release (lesson 16).

:::key-takeaways
- ML CI also tests data, schemas and models. [1]
- Cheap tests: feature-engineering unit tests, training convergence, no NaN values, expected artifacts, component integration. [1]
- CML can post metrics and plots to pull requests from a GitHub Actions workflow. [38]
:::

:::glossary
- **CI (continuous integration)**: automatic build and tests on every change.
- **Unit test**: a small test of one piece of logic.
- **Integration test**: a test that several pieces work together.
- **Contract test**: a test that two components agree on what they send and expect.
- **Threshold test**: a test that a number (like accuracy) stays above a set limit.
- **Bias and fairness**: checking the model does not treat groups of people unfairly.
- **Slices (of data)**: subgroups of the data, such as by country.
- **One-hot encoding**: turning a category into a row of 0/1 columns.
- **Convergence**: the loss steadily decreasing toward a good value during training.
- **Overfit (a few records)**: memorise them; a sanity check that learning works at all.
- **NaN**: "not a number", a broken numeric result that poisons later maths.
- **Artifact**: a file or package a step produces.
- **CML (Continuous Machine Learning)**: a tool that posts ML results to pull requests.
- **GitHub Actions**: GitHub's built-in automation that runs workflows on events like a push.
- **Pull request (PR)**: a proposed change that others review before merging.
- **Runner**: a machine that executes CI jobs.
- **DVC**: a tool for versioning data and pipelines.
:::
