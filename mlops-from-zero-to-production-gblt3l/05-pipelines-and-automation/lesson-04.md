---
id: l20
title: Continuous training and its triggers
quiz: quiz-04.yaml
resources: []
sources: [1, 2]
---
After this lesson you can list the triggers for retraining, say what a training run must record, and name the risk of retraining on data the model influenced.

## What continuous training is

Continuous training (CT) is the property that is unique to ML systems: the system automatically retrains models and serves them. [1] It is the main goal of Level 1: models are trained in production on fresh data through triggers, and the same pipeline runs in development, preproduction and production. [1]

## The triggers

Google lists five ways a pipeline run can start. [1]

1. **On demand**: manually, for an ad hoc run.
2. **On a schedule**: when new, labelled data is systematically available daily, weekly or monthly.
3. **On availability of new training data**: new data becomes available and is not necessarily on a schedule.
4. **On model performance degradation**: the model is retrained when its performance falls.
5. **On significant changes in the data distribution**: concept drift (the real world changing so old patterns stop holding). When the live data changes a lot from what the model was trained on, retraining is triggered.

The first three are about data and time, and are simple to implement. The last two depend on monitoring (chapter 7), which is why Level 1 ends with monitoring feeding the pipeline's triggers. [1]

## What a run does

A triggered run executes the pipeline: data validation (lesson 10), preparation, training, evaluation and model validation (lesson 16). A model that passes is pushed to the model registry, and a model that fails is not. [1] Every run records its metadata (lesson 15), including a pointer to the previous model so you can roll back. [1]

## Risks to design for

**Retraining on what the model caused.** A model can influence its own future training data, directly (its predictions decide which examples are collected) or through hidden loops between systems. The technical-debt paper lists these as feedback loops, and suggests randomisation or isolating part of the data from the model's influence. [2] If your retraining trigger is "new data arrived", ask whether that data was shaped by the previous model.

**A trigger that never stops.** A rule such as "retrain when performance degrades" can fire repeatedly if the degradation is caused by a data problem that retraining cannot fix. A failing data-validation step should stop the run for investigation (lesson 10), not retrain on bad data. [1]

**Cost.** Each run consumes compute and review attention. Pick the least frequent trigger that keeps performance within what the system needs. Rule #8 of the Rules of ML asks how fresh your system must be, which is the question that sets that frequency (lesson 28).

:::key-takeaways
- CT automatically retrains and serves models; it is unique to ML. [1]
- Triggers: on demand, on a schedule, on new data, on performance degradation, on data distribution changes. [1]
- Data-validation failures should stop a run; passing models go to the registry. [1]
- Beware retraining on data the previous model influenced. [2]
:::

:::glossary
- **Continuous training (CT)**: automatically retraining and redeploying models.
- **Trigger**: what starts a retraining run (a click, a schedule, new data, a drop in quality, drift).
- **Ad hoc**: done once, when someone needs it.
- **Labelled data**: examples where the right answer is known.
- **Performance degradation**: the model's quality getting worse.
- **Data distribution**: how the values in the data are spread out.
- **Concept drift**: the relationship the model learned stops being true as the world changes.
- **Preproduction**: the staging environment before production.
- **Model registry**: where passing models are stored.
- **Metadata**: records of what ran and with what.
- **Feedback loop**: the model's own output shaping its future training data.
- **Randomisation**: deliberately showing random choices to avoid the model only ever seeing what it already prefers.
- **Rollback**: switching back to the previous model.
- **Freshness**: how recent the model's training data must be.
:::
