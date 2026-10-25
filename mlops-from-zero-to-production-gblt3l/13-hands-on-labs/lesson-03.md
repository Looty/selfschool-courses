---
id: l51
title: "Lab 3: detect data drift with Evidently"
quiz: quiz-03.yaml
resources: [../resources/lab3-drift-report.py]
sources: [22, 66]
---
After this lab you will have compared a reference dataset with a "production" dataset using an Evidently drift report, exported the result and decided what you would alert on.

This is a hands-on lab. The code follows the Evidently quickstart as fetched on the access date; Evidently's API changes between versions, so match the version in your environment to the page. The ready-made script was run while writing this course (with `pandas<2.3`); the quickstart code below it was not run verbatim.

## Shortcut: the ready-made script

Download `lab3-drift-report.py` from this lesson's Resources. It builds a made-up reference table and a "production" table (older customers and a new country), runs the same `DataDriftPreset` as below and writes `drift_report.html`. It needs no download and was run while writing this course.

```bash
uv venv && uv pip install evidently numpy "pandas<2.3"
python lab3-drift-report.py
```

Use `pandas<2.3`: with the newest pandas, Evidently failed to import in testing. In that test run, 2 of 3 columns drifted (`age` and `country`); `monthly_spend` did not. Check that your result agrees, then read the steps below to see what each line does.

## Step 1: install and import

```python
!pip install evidently
```

```python
import pandas as pd
from sklearn import datasets

from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset
```

The quickstart runs in Jupyter or Colab. Evidently covers prediction quality, input data quality (such as missing values or out-of-range features) and data and prediction drift, and the page notes drift checks are useful because they can flag shifts without ground-truth labels. [66]

## Step 2: define a reference and a "production" set

The example loads the UCI Adult dataset (a public table of census-style records) from OpenML (a public dataset library) and splits it into a reference set (the "normal" data) and a "prod" set (pretend production data). The prod set includes education levels that are missing from the reference, which creates artificial drift for the demonstration. [66] You tell Evidently which columns are numerical and which are categorical with a `DataDefinition`. [66]

```python
schema = DataDefinition(
    numerical_columns=["education-num", "age", "capital-gain", "hours-per-week", "capital-loss", "fnlwgt"],
    categorical_columns=["education", "occupation", "native-country", "workclass", "marital-status", "relationship", "race", "sex", "class"],
)

eval_data_1 = Dataset.from_pandas(pd.DataFrame(adult_prod), data_definition=schema)
eval_data_2 = Dataset.from_pandas(pd.DataFrame(adult_ref), data_definition=schema)
```

The second dataset is the reference that the first is compared against. [66] Getting that order right is the first thing people get wrong.

## Step 3: run the drift report

```python
report = Report([
    DataDriftPreset()
])

my_eval = report.run(eval_data_1, eval_data_2)
```

`DataDriftPreset` checks for statistical distribution changes across all columns, with default tests; methods and thresholds can be customised. Evaluating `my_eval` in a notebook renders the report with scores and test results. [66] Lesson 26 explained that drift tests such as these compare a current window with a reference, and that the choice of test and threshold is yours to defend. [22]

## Step 4: export

```python
# my_eval.json()
# my_eval.dict()
# my_report.save_html("file.html")
```

The results can be exported as a JSON string, a dictionary or an HTML file. [66] JSON is the one a pipeline can read: a scheduled task can run the report, parse the share of drifted columns and decide whether to alert, which connects to the monitoring-by-layer design of lesson 25.

## Step 5: a data summary with tests

```python
report = Report([
    DataSummaryPreset()
],
include_tests="True")
my_eval = report.run(eval_data_1, eval_data_2)
```

`DataSummaryPreset` summarises every column and runs auto-generated tests for data quality and descriptive statistics when tests are enabled. [66]

## Check yourself

- Which columns did the report flag as drifted? Does the result match the fact that the prod set has education levels missing from the reference?
- If a column drifts but the model's accuracy (when labels arrive) is fine, would you retrain? Lesson 27's distinction between data drift and concept drift is the guide.
- For continuous monitoring the quickstart points to the Evidently platform, which can be self-hosted; local reports suit one-off evaluations. [66]

:::low-confidence
The quickstart's API differs from older Evidently versions, and its default drift methods and thresholds are not listed on the page. Check your installed version before trusting a result. [66]
:::

:::key-takeaways
- A drift report compares a current dataset with a reference; keep the argument order straight. [66]
- `DataDriftPreset` runs default drift tests across columns; `DataSummaryPreset` with tests checks quality and statistics. [66]
- Export JSON so a pipeline can act on the result; use the platform for continuous monitoring. [66]
:::

:::glossary
- **Drift**: the current data differing from the reference data.
- **Evidently**: an open-source Python tool for data and model monitoring.
- **Reference dataset**: the "normal" data used as the yardstick.
- **Production ("prod") dataset**: recent live data being checked.
- **pandas / DataFrame**: Python's table library / its table object.
- **Jupyter / Colab**: notebook environments where you run code in chunks and see results inline.
- **OpenML**: a public library of datasets.
- **Data definition / schema**: telling the tool which columns are numbers and which are categories.
- **Numerical / categorical column**: a column of numbers / of labels such as "country".
- **Preset**: a ready-made bundle of checks (`DataDriftPreset`, `DataSummaryPreset`).
- **Report**: Evidently's object that runs checks and shows results.
- **Ground truth**: the real outcomes, not available yet in live monitoring.
- **Data quality**: whether data is complete, in range and consistent.
- **Statistical distribution**: how often each value occurs.
- **JSON / HTML export**: machine-readable / human-readable saved results.
- **Data drift vs concept drift**: inputs changed vs the meaning of inputs changed.
- **Self-hosted**: run on your own server.
:::
