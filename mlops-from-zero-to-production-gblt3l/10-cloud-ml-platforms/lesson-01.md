---
id: l37
title: Managed pipelines with Amazon SageMaker
quiz: quiz-01.yaml
resources: []
sources: [52]
---
After this lesson you can read a SageMaker pipeline as a DAG, name its step types, and say how it maps onto the pipeline ideas of chapter 5.

## What it is

Amazon SageMaker is Amazon's managed service for building, training and deploying ML models: you rent the platform instead of running the tools yourself. A SageMaker pipeline is a series of connected steps arranged as a DAG (a one-way flowchart with no loops). You define it with a drag-and-drop UI, with the Pipelines SDK (a Python library), or as a JSON file that describes the steps and how they relate. [52]

The shape of the graph is decided the same way as in DVC (lesson 17): by data dependencies. They are created when a property of one step's output is passed as input to another step. [52] You do not list an order; the order falls out of what consumes what.

## The documentation's example pipeline

The overview walks through one pipeline built on the abalone dataset. Reading it step by step is the fastest way to learn the vocabulary. [52]

1. `AbaloneProcess` is a **Processing** step that runs a preprocessing script, for example filling missing values, normalising numbers or splitting into train, validation and test sets.
2. `AbaloneTrain` is a **Training** step that configures hyperparameters and trains a model from the preprocessed data.
3. `AbaloneEval` is another Processing step that evaluates the model. It uses the test dataset produced by `AbaloneProcess`, which is the page's example of a data dependency.
4. `AbaloneMSECond` is a **Condition** step. It checks that the mean-square error of the evaluation is below a limit; if the model does not meet the criteria, the pipeline run stops.
5. If it passes, `AbaloneRegisterModel` calls a **RegisterModel** step that registers the model as a versioned model package group in the SageMaker Model Registry, `AbaloneCreateModel` calls **CreateModel** to prepare for batch transform, and `AbaloneTransform` calls **Transform** to generate predictions on a dataset you specify.

Compare it with lessons 16 and 19. The Condition step is a release gate: validation against a threshold decides whether the next steps run. The RegisterModel step is the registry hand-off. The pipeline is one place where the "train, evaluate, gate, register" loop becomes executable.

## What else the platform lists

The overview lists further topics that this lesson only names, because their pages were not read: pipeline parameters, a `@step` decorator for lifting Python code into a step, passing data between steps, caching (next lesson), retry policy, selective execution, `ClarifyCheck` and `QualityCheck` steps for baselines and drift detection, scheduling with EventBridge, integration with SageMaker Experiments, local mode and troubleshooting. [52]

The `ClarifyCheck` and `QualityCheck` names are worth noting, because they show a managed platform putting data-quality and drift checks inside the pipeline, the same role that TFDV and Evidently play in the open-source stack (lessons 10 and 26). What exactly they compute is not described on the page used here. [52]

## Mapping to what you know

| Idea from this course | In a SageMaker pipeline |
| --- | --- |
| Pipeline as a DAG (lesson 17) | Steps connected by data dependencies [52] |
| Validation gate (lesson 16) | Condition step stops the run if the metric misses the limit [52] |
| Model registry (lesson 14) | RegisterModel into a versioned model package group [52] |
| Drift and quality checks (lesson 26) | ClarifyCheck and QualityCheck steps (details not read) [52] |

:::low-confidence
This lesson is based on the overview page only. The step-type details, parameter handling and the exact checks performed by `ClarifyCheck` and `QualityCheck` are on pages that were not read. [52]
:::

:::key-takeaways
- A SageMaker pipeline is a DAG whose structure comes from data dependencies between steps. [52]
- The documentation's example is process, train, evaluate, condition, register, then create model and transform. [52]
- A Condition step is the managed form of a release gate: it stops the run if the metric misses its limit. [52]
:::

:::glossary
- **Managed platform**: a cloud service where the provider runs the infrastructure and tools for you.
- **Amazon SageMaker**: Amazon's managed ML platform.
- **Pipeline / DAG**: connected steps run in dependency order, with no loops.
- **Pipelines SDK**: the Python library for defining SageMaker pipelines.
- **JSON definition**: the pipeline described as a JSON text file.
- **Data dependency**: step B needs a result from step A, so A runs first.
- **Processing step**: runs a script for data work such as cleaning and splitting.
- **Training step**: trains a model.
- **Condition step**: an if-check that decides whether the pipeline continues.
- **RegisterModel step**: saves the model as a new version in the registry.
- **CreateModel / Transform steps**: package the model, then run batch predictions with it.
- **Model package group**: a named collection of versions of one model.
- **Hyperparameters**: training settings chosen in advance.
- **Mean-square error (MSE)**: the average of the squared prediction errors; lower is better.
- **Abalone dataset**: a classic example dataset predicting sea-snail age.
- **ClarifyCheck / QualityCheck**: steps that check bias or data quality and drift against a baseline.
- **EventBridge**: AWS's service for scheduling and reacting to events.
- **Release gate**: a check a model must pass before it goes on.
:::
