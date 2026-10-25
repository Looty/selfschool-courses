---
id: l13
title: Experiment tracking with MLflow
quiz: quiz-01.yaml
resources: []
sources: [1, 5]
---
After this lesson you can record a training run with MLflow, say where its data is stored, and find the best run from code.

## Why track experiments

Google lists experimentation as a difference between ML and other software: you try features, algorithms, modelling techniques and parameters, and the difficulty is tracking what worked while keeping runs reproducible and reusable. [1] An experiment tracker is a lab notebook that writes itself: it answers "which settings and data produced this result?" without anybody having to remember.

## Core concepts

MLflow Tracking is an API and UI for recording what happens when you run ML code and for reviewing it later. [5]

- A **run** is one execution of your code, such as one `python train.py`. It stores metadata (metrics, parameters, start and end times) and artifacts (output files such as model weights or images).
- An **experiment** groups the runs and models for one task.
- **Tags** are arbitrary labels on runs that let you filter and search.
- **Models** are trained artifacts logged during runs, and a dataset can be attached to a run with `mlflow.log_input()`.

## Logging a run

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("lr", 0.001)
    # your training code
    mlflow.log_metric("val_loss", val_loss)
```

Autologging removes most explicit calls: call `mlflow.autolog()` before your training code. It supports libraries such as scikit-learn, XGBoost, PyTorch, Keras and Spark. [5]

## Finding the best run

`MlflowClient` exposes the same operations as the UI. The documentation's example finds the run with the lowest validation loss: [5]

```python
client = mlflow.tracking.MlflowClient()
best_run = client.search_runs("0", order_by=["metrics.val_loss ASC"], max_results=1)[0]
print(best_run.data.metrics)
```

The UI lets you browse and compare runs, search by parameter or metric values, visualise metrics over time and download artifacts. [5]

## Where the data lives

Three pieces make up the setup. [5]

- The **backend store** is the small-records drawer: it keeps run metadata (IDs, times, parameters, metrics) in files or a database such as PostgreSQL.
- The **artifact store** is the big-files drawer: model weights, images and data files. By default it writes to a local `mlruns` folder, and it also supports cloud storage like Amazon S3 and Azure Blob Storage.
- The **tracking server** is optional: a web server in front of both drawers that offers an API and the UI, and can let a whole team share them.

By default no server is needed; runs are logged to the local `mlruns` directory. A single laptop is fine for exploration; a team needs the server and shared stores, which is the point where tracking becomes infrastructure you operate.

## Habits that make tracking useful

- Log the parameters that define the run and the metric you will use to compare runs, with the same names every time.
- Log the dataset or its version (lesson 9) next to the parameters.
- Treat the tracking server like any stateful service: back up the backend store and artifact store.

:::key-takeaways
- A run is one execution; an experiment groups runs; parameters, metrics and artifacts are logged per run. [5]
- `mlflow.autolog()` covers common libraries; `MlflowClient.search_runs` finds runs programmatically. [5]
- Backend store for metadata, artifact store for files, optional tracking server for teams. [5]
:::

:::glossary
- **Experiment tracking**: automatically recording what you tried and what happened, so you can compare attempts.
- **MLflow**: an open-source tool for tracking runs and managing models.
- **Run**: one execution of your training code, with its settings and results saved.
- **Experiment (in MLflow)**: a folder of related runs for one task.
- **Parameter**: a setting you chose for the run, such as the learning rate.
- **Learning rate (`lr`)**: how big a step training takes each time it adjusts the model.
- **Metric**: a score recorded for the run, like validation loss.
- **Validation loss**: how wrong the model is on the validation data.
- **Artifact**: an output file of a run, such as model weights.
- **Weights**: the numbers inside a model that training adjusted.
- **Tag**: a free-form label on a run for filtering.
- **Autologging**: MLflow recording the usual things for you with one line.
- **Backend store / artifact store / tracking server**: the records drawer, the big-files drawer and the optional shared web front.
- **REST API**: a standard web interface programs use to ask for things.
- **PostgreSQL**: a widely used database.
- **Stateful service**: a service that holds data you must keep and back up.
:::
