---
id: l04
title: "MLOps maturity levels"
quiz: quiz-04.yaml
resources: []
sources: [1, 15]
---
After this lesson you can place a team on Google's levels 0 to 2 and Microsoft's levels 0 to 4, and name what the next step up looks like.

## Why levels help

This lesson names many components (feature store, model registry, pipeline orchestrator) that later chapters explain one by one. You do not need to understand each one yet; for now, notice only how the levels change from "a person does every step by hand" to "the system does it and watches itself".

Maturity models let you assess where a team is and plan the next increment instead of facing the full complexity at once. Microsoft says so directly: use the model to develop MLOps capability gradually. [15] Google makes the same point: teams can adopt the practices step by step. [1]

## Google's three levels

**Level 0: manual process.** Every step is manual and script-driven, often run in notebooks, and the transition between steps is manual too. Data scientists hand a trained model file to engineers, which can cause training-serving skew (the model sees differently prepared data in production than it did in training). Releases are infrequent, perhaps a couple of times a year. There is no CI and no CD, only the prediction service is deployed, and nothing actively monitors the model's performance. [1]

**Level 1: ML pipeline automation.** The goal is continuous training of the model by automating the pipeline, which also enables continuous delivery of the prediction service. The pipeline is orchestrated, models retrain on fresh data through triggers, the same pipeline runs in development, preproduction and production, and components are modular and containerized. The whole training pipeline is deployed, not just the model. Added components are data validation, model validation, an optional feature store, metadata management and pipeline triggers. The remaining weakness is that new pipelines are still tested and deployed manually, which does not scale across many pipelines. [1]

**Level 2: CI/CD pipeline automation.** The pipeline itself is built, tested and deployed automatically, so data scientists can try new feature engineering, architectures and hyperparameters quickly. The core components are source control, test and build services, deployment services, a model registry, a feature store, an ML metadata store and a pipeline orchestrator. [1]

## Microsoft's five levels

Microsoft's model has five levels. [15]

| Level | Name | A sign you are there |
| --- | --- | --- |
| 0 | No MLOps | Builds, deployments and training are manual; performance tracking is not centralized |
| 1 | DevOps but no MLOps | Application builds are automated and code is version controlled, but results are hard to trace and reproduce |
| 2 | Automated training | Training is automated and tracked, models are easy to reproduce, releases are still manual |
| 3 | Automated model deployment | Releases are automatic, with traceability from deployment back to the original data |
| 4 | Full MLOps automated operations | The system is monitored, and drift or regression signals can trigger retraining |

Microsoft also notes that in practice an organization often shows traits of more than one level at once, so treat the levels as a continuum rather than isolated stages. [15]

## Using the levels

Both models agree on the order of the climb: first make training repeatable, then make releases automatic, then close the loop with monitoring. A level is not a goal in itself. A model retrained twice a year by one person may not justify Level 2 machinery. The levels tell you what the next missing capability is and why a team would want it.

:::low-confidence
Google's levels (0 to 2) and Microsoft's levels (0 to 4) are two different scales from two vendors. They do not map one-to-one, so do not compare levels across them directly. [1][15]
:::

:::key-takeaways
- Google: Level 0 manual, Level 1 pipeline automation (continuous training), Level 2 CI/CD of the pipeline itself. [1]
- Microsoft: 0 no MLOps, 1 DevOps but no MLOps, 2 automated training, 3 automated model deployment, 4 full automated operations. [15]
- Use a maturity model to find the next missing capability, and expect overlap between levels. [15]
:::

:::glossary
- **Maturity model**: a ladder of levels that shows how advanced a team's practice is and what to build next.
- **Notebook**: an interactive document mixing code, output and notes; popular with data scientists, awkward to automate.
- **Training-serving skew**: the model gets data prepared one way in training and another way in production, so it performs worse than expected.
- **Orchestrated pipeline**: a pipeline run and supervised by a tool that decides what runs when.
- **Trigger**: an event that starts a pipeline, such as new data or a schedule.
- **Containerized**: packaged with everything it needs so it runs the same anywhere (for example in Docker).
- **Data validation**: automatic checks that incoming data looks as expected.
- **Model validation**: an automatic check that a new model is good enough to replace the old one.
- **Feature store**: a shared, versioned place where model inputs are computed and stored once and reused.
- **Metadata store**: a log of what ran, with which data and settings, and what came out.
- **Model registry**: a catalogue of trained model versions and which one is live.
- **Drift**: the real-world data changing so the model's training no longer matches reality.
- **Regression**: a new version doing worse than the old one.
- **Source control**: a system such as Git that tracks every change to files.
:::
