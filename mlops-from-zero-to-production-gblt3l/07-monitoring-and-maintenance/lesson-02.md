---
id: l26
title: Drift detection in practice
quiz: quiz-02.yaml
resources: []
sources: [19, 21, 22]
---
After this lesson you can configure a drift check, explain why its defaults depend on data size and column type, and say what a drift alert does and does not mean.

## Reference and current

Drift means the data has changed. Every drift check compares two datasets: a **reference** (what the model was trained on, or a period known to be good) and a **current** dataset (recent production data). Evidently requires both, and the columns tested must not be empty in either. [22] Choosing the reference is a design decision: the training set tests whether production still looks like training, while a recent healthy window tests for sudden change.

Evidently is an open-source (Apache 2.0) framework for evaluating, testing and monitoring data and AI systems, available as a Python library and as a self-hosted platform. [21]

## The default tests

Evidently checks each column separately and picks the test from the column type and the reference size. [22]

| Reference size | Column type | Default test | Drift when |
| --- | --- | --- | --- |
| 1,000 rows or fewer | Numerical, more than 5 unique values | Two-sample Kolmogorov-Smirnov test | p-value ≤ 0.05 |
| 1,000 rows or fewer | Categorical, or numerical with 5 or fewer unique values | Chi-squared test | p-value ≤ 0.05 |
| 1,000 rows or fewer | Binary categorical | Proportion difference test (Z-score) | p-value ≤ 0.05 |
| More than 1,000 rows | Numerical, more than 5 unique values | Wasserstein distance | distance ≥ 0.1 |
| More than 1,000 rows | Categorical, or numerical with 5 or fewer unique values | Jensen-Shannon divergence | divergence ≥ 0.1 |

The reason for the split is visible in the table. For small data the score is a p-value (the probability of seeing a difference this big by pure chance), so a lower value means drift. For large data it is a distance or divergence (a plain "how far apart are the two distributions"), so a higher value means drift. [22] For text, Evidently trains a domain classifier to tell reference and current texts apart and uses its ROC AUC, with drift above 0.55 for large data. [22]

You can change the logic. The documentation lists PSI, Kullback-Leibler divergence, Jensen-Shannon distance and Wasserstein distance among the available methods, and lets you set thresholds or pass a custom test. [22]

## From columns to a dataset verdict

Per-column results can be rolled up. Presets such as `DatasetDriftPreset` and metrics such as `DriftedColumnsCount` apply a rule on top, for example declaring dataset drift when 50% of features drift. The page's examples show this share-based rule and you can set your own threshold; it does not state a default share. [22]

## Behaviours to know

- Empty and infinite values are filtered out before computing drift. [22]
- By default, drift tests do not react to changes in the number of nulls, so you need separate tests on missing values. [22]
- TFDV measures drift between consecutive spans of data, using L-infinity distance for categorical features and approximate Jensen-Shannon divergence for numeric ones, with a threshold you set; choosing a good threshold usually takes iteration and domain knowledge. [19]

## What a drift alert means

Drift says the data changed. It does not say the model got worse. A feature can drift without affecting predictions, and a model can degrade with no feature drift if the relationship between inputs and the target changes (lesson 27). Treat drift as a prompt to look: check the affected features, compare prediction distributions, and look at quality metrics if labels are available. Tune thresholds so that an alert is rare enough to be read, using the iteration TFDV's guide recommends. [19]

:::key-takeaways
- Drift checks compare a reference with a current dataset. [22]
- Evidently's defaults depend on column type and reference size: KS or chi-squared for small data, Wasserstein or Jensen-Shannon for large. [22]
- Dataset-level drift is a rule over the share of drifting columns; you choose the threshold. [22]
- Drift means the data changed, not that the model got worse. [19][22]
:::

:::glossary
- **Drift**: the production data differing from the data you compare it with.
- **Reference dataset**: the "normal" data used as the yardstick, often the training data.
- **Current dataset**: recent production data being checked.
- **Evidently**: an open-source Python tool for data and model monitoring.
- **Apache 2.0**: a permissive open-source licence.
- **Kolmogorov-Smirnov (KS) test**: a statistical test of whether two sets of numbers come from the same distribution.
- **Chi-squared test**: a test of whether category counts differ from what you would expect.
- **Z-score / proportion difference test**: a test comparing two percentages.
- **p-value**: the chance of a difference this large arising by luck; small means "probably real".
- **Wasserstein distance**: how much "effort" it takes to reshape one distribution into the other.
- **Jensen-Shannon divergence**: a symmetric score of how different two distributions are, from 0 (same) upward.
- **PSI (population stability index)**: a score used in banking for how much a distribution shifted.
- **Kullback-Leibler divergence**: another measure of how one distribution differs from another.
- **Domain classifier**: a model trained to tell reference data from current data; if it can, they differ.
- **ROC AUC**: a score from 0.5 (guessing) to 1 (perfect) for how well a classifier separates two groups.
- **Preset**: a ready-made bundle of checks.
- **Null**: a missing value.
:::
