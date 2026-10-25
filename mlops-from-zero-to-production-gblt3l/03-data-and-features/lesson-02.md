---
id: l10
title: "Data validation: schemas, skew and drift"
quiz: quiz-02.yaml
resources: []
sources: [1, 2, 19]
---
After this lesson you can describe what a data validation step checks, tell skew from drift, and explain why a failing check should stop the pipeline.

## Why data needs tests

In ML systems, data does the job code used to do, so the technical-debt paper asks for sanity checks on incoming data and monitoring for shifts in distribution (how the values are spread out). [2] Google's Level 1 pipeline puts a data validation step before training. A mismatch with the expected schema, such as unexpected, missing or wrongly valued features, stops the pipeline so the data scientists can investigate. A shift in the statistical properties of the data, a data value skew, triggers retraining. [1]

TensorFlow Data Validation (TFDV) is a library for this. It can analyse data before any model is trained, identify anomalies in training and serving data, infer a schema automatically, and detect training-serving skew and data drift. [19]

## Statistics, schema, anomalies

**Statistics.** TFDV computes statistics over each dataset, such as value distributions, missing counts, value-list lengths and minimum and maximum values. [19]

**Schema.** A schema codifies expectations: data types, categorical values, which features are present. You can have one inferred from statistics: [19]

```python
schema = tfdv.infer_schema(statistics=train_stats)
tfdv.display_schema(schema=schema)
```

The inferred schema is best-effort and only captures basic properties. Review it, change it as needed, version it, and push it into the pipeline explicitly. [19]

**Anomalies.** Comparing statistics against the schema finds anomalies such as unexpected types, out-of-range values and missing features. Schema *environments* let expectations differ by context; for example a label feature can be required when training and absent when serving. [19]

## Skew and drift

The two words are used for different comparisons. [19]

- **Training-serving skew** (distribution skew) means the distribution of feature values in training data differs significantly from the serving data. Causes include training on a different corpus than the one served, and faulty sampling that keeps only a subsample of serving data or downsamples without appropriate upweighting.
- **Drift** is measured between consecutive spans of data, such as one day of data against the next. TFDV scores the difference with a distance measure (L-infinity for categories, approximate Jensen-Shannon divergence for numbers; both are just "how different are these two distributions") and warns when the score exceeds a threshold you set. Choosing a good threshold usually takes trial and error and knowledge of your domain.

Skew compares training with serving. Drift compares the past with the present within one stream. Both are about the data, not the model, so you can run them without any labels.

## Where validation runs

In a TFX pipeline TFDV is invoked on every split from the example generator and on the data before and after the transform step. [19] The general pattern for any tool: validate when data enters, validate again when it is turned into features, stop on schema problems, and alert or retrain on distribution shifts. [1][19]

:::low-confidence
TFDV is one tool, and it is the only validation library read for this course. The concepts of schema checks, skew and drift are general; the function names are TFDV's. [19]
:::

:::key-takeaways
- A schema violation should stop the pipeline; a distribution shift can trigger retraining. [1]
- TFDV infers a schema from statistics, but the inferred schema is only a best-effort starting point that you review and version. [19]
- Skew compares training with serving data; drift compares consecutive spans of data. [19]
:::

:::glossary
- **Data validation**: automatic checks that data looks the way you expect before it is used.
- **Schema**: the list of expected columns, their types and allowed values.
- **Anomaly**: something that breaks the expectations, such as a missing column or an impossible value.
- **Distribution**: how often each value (or range of values) occurs in the data.
- **Training-serving skew**: training data and live data look different.
- **Drift**: the data changing over time.
- **TFDV (TensorFlow Data Validation)**: Google's library for computing data statistics, schemas and anomaly checks.
- **TFX**: Google's toolkit for building production ML pipelines.
- **Categorical feature**: an input that is a label, like "country".
- **Numeric feature**: an input that is a number, like "age".
- **Divergence / distance**: a number measuring how different two distributions are.
- **Threshold**: the limit that triggers a warning when crossed.
- **Downsampling / upweighting**: keeping only some examples, then counting each kept one more heavily to make up for it.
- **Corpus**: a body of data (originally of text).
- **Labels**: the known correct answers; drift checks do not need them.
:::
