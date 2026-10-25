---
id: l32
title: A reference architecture and your adoption roadmap
quiz: quiz-04.yaml
resources: []
sources: [1, 2, 13, 15]
---
After this lesson you can sketch a reference architecture for an ML system, order the capabilities you would build first, and judge which parts a given team needs.

## The picture to keep in mind

The components around the model code, from the first chapter, are the system. Here they are again, now with the lesson that covered each.

![Nine boxes around a small box labelled Model code. Around it: data validation, feature store, metadata store, pipeline orchestrator, model validation, model registry, prediction service and monitoring.](../resources/ml-system.svg)

| Component | What it does | Lesson |
| --- | --- | --- |
| Data validation | Stops the pipeline on schema problems; flags drift | 10 |
| Feature store | One definition of features for training and serving | 11, 12 |
| Metadata store | Records each run: versions, parameters, artifacts, metrics | 13, 15 |
| Pipeline orchestrator | Runs the steps as a DAG on triggers | 17, 20 |
| Model validation | Gate: beat the baseline, per-segment checks, compatibility | 16 |
| Model registry | Versions and aliases for deployment | 14 |
| Prediction service | Online, batch or embedded serving with safe rollout | 21 to 24 |
| Monitoring | Service, data and model signals that trigger action | 25 to 28 |

These are the components Google lists for Level 1 and Level 2 pipelines. [1] Only a small part of the system is model code. [2]

## Order of adoption

Google and Microsoft agree on the order of the climb. Both start by making training repeatable and tracked, move to automatic releases, then close the loop with monitoring. [1][15] A practical roadmap, using your own judgement on the details:

1. **Baseline and plumbing first.** A simple model, shared feature code, consistent training and serving (Rules #1, #4, #32). [13]
2. **Make runs reproducible and tracked.** Data versioning, experiment tracking, a model registry (chapters 3 and 4). Microsoft's Level 2 is "automated training": training is managed and traceable, models are easy to reproduce, and releases are still manual. [15]
3. **Automate the pipeline.** Orchestrated steps, data validation, model validation and triggers: Google's Level 1. [1]
4. **Automate releases.** CI/CD for the pipeline and for model deployment, with canaries and approvals: Google's Level 2; Microsoft's Level 3. [1][15]
5. **Close the loop.** Monitoring that triggers investigation and retraining: Microsoft's Level 4. [15]

## How much do you need?

Maturity is not a score to maximise. Match it to the system:

- One model retrained a few times a year, with a small blast radius, may stop at a tracked, reproducible, manually released process with good monitoring.
- Many models, fast-changing data or high-stakes decisions justify the automation and governance of the later levels.

Two questions help. How fast does performance decay (Rule #8)? And what does a wrong prediction cost? [13] The first sets how automated retraining must be; the second sets how strict validation and approval must be. This reasoning is the course's own, built on those sources.

## A design exercise

Take a use case you know, say a churn model, a fraud score or a recommender, and answer in a page:

- What is the baseline, and what would you measure to know the model beats it?
- Which data and features, and where do the training and serving paths share code?
- Which records do you keep for each run and each release?
- Where are the gates and who approves what?
- What do you monitor in each of the three layers, and what pages a human?
- What is your rollback, and how fast can you do it?

The final quiz asks you to do a short version of this.

:::key-takeaways
- The system is the model code plus data validation, a feature store, metadata, orchestration, validation, a registry, serving and monitoring. [1]
- Adopt in order: baseline and plumbing, reproducibility and tracking, pipeline automation, release automation, closed-loop monitoring. [1][13][15]
- Match maturity to decay speed and the cost of being wrong. [13]
:::

:::glossary
- **Reference architecture**: a standard blueprint of the parts a system like this usually has.
- **Data validation**: automatic checks on incoming data.
- **Feature store**: shared, consistent model inputs for training and serving.
- **Metadata store**: the record of every run.
- **Pipeline orchestrator**: the tool that runs pipeline steps in order, on triggers.
- **DAG**: a one-way flowchart of steps.
- **Model validation**: a gate a new model must pass.
- **Model registry**: a catalogue of model versions and which is live.
- **Prediction service**: the running model other programs call.
- **Baseline**: the simple model or rule to beat.
- **Plumbing**: the supporting code and systems around the model.
- **Decay**: how fast model quality drops as the world changes.
- **Blast radius**: how many users a failure affects.
- **Churn model**: predicts which customers are about to leave.
- **Fraud score**: a number saying how likely a transaction is fraudulent.
- **Recommender**: a model that suggests items a user may like.
:::
