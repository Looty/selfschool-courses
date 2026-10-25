---
id: l52
title: "Capstone: design the loop for a model you choose"
quiz: quiz-04.yaml
resources: []
sources: [1, 6, 38, 64, 65, 66]
---
After this capstone you will have a written design, using the tools from the labs, for taking one real model from data to monitoring, and a list of what you would still need to find out.

This lesson has no new facts; it asks you to combine what you have done. Pick a model you care about: a churn predictor, a demand forecast, a document classifier. The check below is a design document, graded against a rubric, so spend the time it needs.

## The loop to design

Google's description of automated ML pipelines includes triggers for retraining, validation of data and models, a registry and monitoring. [1] Your design should name a concrete tool for each part. Use the tools from the labs where you can.

1. **Data.** Which files or tables are versioned, and how? With DVC you track the data with `dvc add`, commit the `.dvc` file and push to a remote, and anyone can get the matching version with `dvc pull`. [65]
2. **Experiments.** What does every training run log? With MLflow: parameters, metrics and the model, plus tags for the code and data versions you add yourself. [64]
3. **Pipeline.** Which stages, and what re-runs when something changes? A `dvc.yaml` with stages whose `deps`, `params` and `outs` form the graph. [6]
4. **Gate.** What must a candidate beat before it ships (lessons 7 and 16)? State the baseline and the thresholds.
5. **CI.** What runs on a pull request? CML can post a report to a pull request with `cml comment create`, so reviewers see the metrics next to the diff. [38]
6. **Release.** How does a version reach production and roll back (lessons 14 and 23)?
7. **Monitoring.** Which signals at system, data and model level (lesson 25), and which drift report runs on which schedule? An Evidently report can be exported as JSON for a pipeline to read. [66]
8. **Response.** What happens when an alert fires: roll back, retrain, fall back (lesson 28)?

## Write it as a table

A good design fits one page. Use these columns: part, tool, what is recorded, what triggers it, who is told on failure. A row with an empty "who is told" cell is a gap.

| Part | Tool | Recorded | Trigger | Who is told |
| --- | --- | --- | --- | --- |
| Data | DVC | `.dvc` file in Git, data in the remote | New data lands | Data owner |
| Experiment | MLflow | Params, metrics, model, code and data tags | Each training run | Author |
| Pipeline | `dvc repro` | Outputs, parameters | Change to deps or params | CI log |
| Gate | Validation step | Candidate versus baseline | Before registration | Reviewers via CML |
| Monitoring | Evidently | JSON drift result | Schedule | On-call |

The table above is an example shape, not a prescription.

## What to flag as unknown

Every design has parts you cannot fill from what you know. Write them down: the real cost of retraining, how fast your data drifts, whether labels arrive and when, who is on call. Those are the questions to answer in the first month of running it; the sources used here cannot answer them for your system.

:::low-confidence
This capstone is an exercise, not a tested reference design. The tools named are the ones this course used; other tools can fill the same roles. [1]
:::

:::key-takeaways
- A design names a tool, a record, a trigger and an owner for every part of the loop. [1]
- Reuse the lab tools: DVC for data and pipelines, MLflow for runs, CML for review, Evidently for drift. [6][38][64][65][66]
- Write down the unknowns; they are your first month's work.
:::

:::glossary
- **Capstone**: a final project that combines everything you learned.
- **Churn predictor**: a model that guesses which customers will leave.
- **Demand forecast**: a model that predicts how much of something will be needed.
- **Document classifier**: a model that sorts documents into categories.
- **Loop (data to monitoring)**: the full cycle of data, training, release and watching, feeding back into the start.
- **Trigger**: the event that starts a step.
- **Gate**: a check a candidate must pass to continue.
- **Baseline**: the reference to beat.
- **CI**: automatic checks on every change.
- **CML**: a tool that posts ML results onto pull requests.
- **Pull request**: a proposed change others review.
- **Registry**: the catalogue of model versions.
- **Rollback**: returning to the previous version.
- **On-call**: the person responsible for responding to alerts right now.
- **Rubric**: a written scoring guide.
:::
