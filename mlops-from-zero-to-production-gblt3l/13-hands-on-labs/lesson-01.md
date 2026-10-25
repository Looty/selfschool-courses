---
id: l49
title: "Lab 1: track an experiment with MLflow"
quiz: quiz-01.yaml
resources: [../resources/lab1-mlflow-train.py]
sources: [64]
---
After this lab you will have run MLflow's tracking server locally, logged a model automatically and by hand, and loaded it back for prediction.

This is a hands-on lab: do the steps on your own machine, then answer the check. The ready-made script below was run end to end while writing this course. The step-by-step commands further down follow the MLflow quickstart, which does not show the output of each command, and were not run verbatim. Budget extra time beyond the estimate shown for the lesson.

## Shortcut: the ready-made script

Download `lab1-mlflow-train.py` from this lesson's Resources. It does steps 2, 4 and 5 below in one file, uses the Iris data that ships with scikit-learn (no internet needed), and was run end to end while writing this course. Set up and run it like this:

```bash
uv venv && uv pip install mlflow scikit-learn
python lab1-mlflow-train.py        # run 1: max_iter=200
python lab1-mlflow-train.py 2      # run 2: max_iter=2, a deliberately bad run
mlflow ui --port 5000              # open http://localhost:5000 and compare the two runs
```

In a test run the first gave accuracy 1.000 and the second about 0.37, so the comparison in step 4 is easy to see. The steps below explain what each part does, if you would rather type it yourself.

## Step 1: install and name an experiment

```bash
pip install mlflow
```

```python
import mlflow
mlflow.set_experiment("MLflow Quickstart")
```

The quickstart says MLflow is available on PyPI and creates the experiment the runs will be grouped under. [64]

## Step 2: train with autologging

Load the Iris dataset (a classic small dataset of flower measurements), split it into training and test sets and define hyperparameters, the training settings (`solver`: the maths method used; `max_iter`: the most steps allowed; `random_state`: the random seed). Then turn on scikit-learn autologging and train as usual. [64]

```python
import mlflow
mlflow.sklearn.autolog()
lr = LogisticRegression(**params)
lr.fit(X_train, y_train)
```

The page describes autologging as "just one line of additional code". It saves the model and logs its parameters and metrics. [64] Compare lesson 13: tracking is only useful if it is automatic enough that nobody skips it.

## Step 3: start the server and look at the run

```bash
mlflow server --port 5000
```

Open `http://localhost:5000` (or the port you chose), go to the "MLflow Quickstart" experiment, select the run and check the logged model and its artifacts. [64] Things to look for: the parameters you set, the metrics autologging recorded, and the model artifact folder.

## Step 4: log by hand

Autologging decides what to record. When you need control, start a run and log each item explicitly. [64]

```python
with mlflow.start_run():
    mlflow.log_params(params)
    lr = LogisticRegression(**params)
    lr.fit(X_train, y_train)
    model_info = mlflow.sklearn.log_model(sk_model=lr, name="iris_model")
    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.set_tag("Training Info", "Basic LR model for iris data")
```

Run it twice with a different `max_iter` and compare the two runs in the UI. This is the exercise that makes experiment tracking click: two numbers you can put side by side, with the parameters that produced them.

## Step 5: load the model back

```python
loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)
predictions = loaded_model.predict(X_test)
```

The `pyfunc` flavor gives a generic prediction interface; `mlflow.sklearn.load_model(model_info.model_uri)` loads it as a native scikit-learn model instead. [64] This is the packaging contract of lesson 15 in action: a consumer does not need to know which library trained the model.

## Check yourself

- Which of your runs has the higher accuracy, and which parameter explains it?
- If a teammate asked you to reproduce the better run next month, what else would you need besides the parameters (lessons 8 and 9)? The quickstart logs parameters, metrics and the model; whether it also records the code version and data version is not stated on the page, so record them yourself as tags.

:::low-confidence
The quickstart does not show command output, and only the ready-made script was run, not every quickstart step. If a step fails on your machine, check the current MLflow documentation; the page was read as of the access date in the sources list. [64]
:::

:::key-takeaways
- `mlflow.sklearn.autolog()` logs a model's parameters and metrics with one line. [64]
- `mlflow server --port 5000` starts the tracking UI where you compare runs. [64]
- `mlflow.start_run()` with `log_params`, `log_metric`, `log_model` and `set_tag` gives manual control. [64]
- Load a logged model with `mlflow.pyfunc.load_model(model_uri)`. [64]
:::

:::glossary
- **Lab**: a hands-on exercise you run on your own machine.
- **MLflow**: an open-source tool for tracking runs and managing models.
- **PyPI / `pip`**: Python's public package index / the installer that fetches from it.
- **Experiment**: a named group of related runs.
- **Run**: one execution of training code, with everything it recorded.
- **Iris dataset**: a tiny classic dataset (flower measurements) used for demos.
- **scikit-learn (sklearn)**: a widely used Python library of classic ML algorithms.
- **Logistic regression**: a simple model that predicts categories.
- **Hyperparameter**: a setting chosen before training.
- **Autologging**: MLflow automatically recording parameters, metrics and the model.
- **Tracking server / UI**: the local web app for browsing runs.
- **Artifact**: a file saved with a run, such as the model.
- **Metric / accuracy**: a score / the share of predictions that were right.
- **Tag**: a free-text label on a run.
- **Model URI**: the address string used to load a saved model.
- **`pyfunc` flavor**: MLflow's library-independent way to load a model and call `predict`.
- **Reproduce**: get the same result again from the record.
:::
