---
id: l12
title: "Training-serving skew: causes and measurement"
quiz: quiz-04.yaml
resources: []
sources: [1, 13, 19]
---
After this lesson you can name the causes of training-serving skew, apply the main rules that prevent it, and measure it at three points.

## Definition and causes

The Rules of Machine Learning define training-serving skew as a gap between how the model performs during training and how it performs when serving real traffic: it looked great in the lab and worse in the field. It can come from a discrepancy between how data is handled in the training and serving pipelines, from a change in the data between training and serving, or from a feedback loop between the model and the system. [13]

Google's maturity guide points at an organisational cause too: at Level 0 data scientists hand a trained model artifact to engineers, and the disconnect between the two can cause skew. [1] TFDV adds two data causes of distribution skew: training on a different corpus than the one you serve, and faulty sampling that keeps only a subsample of serving data or downsamples without appropriate upweighting. [19]

## The rules that prevent it

These rules from the guide are the most practical part. [13]

- **Rule #29: log the features used at serving time and reuse them for training.** This can improve quality and reduce code complexity.
- **Rule #30: importance-weight sampled data; don't arbitrarily drop it.** If you sample, weight the sample to compensate.
- **Rule #31: if you join data from a table at training and serving time, the table may change.** Log features at serving time, or snapshot slowly changing tables.
- **Rule #32: re-use code between your training pipeline and your serving pipeline whenever possible.** Shared transformation code removes a major source of skew, and using one language for both helps.
- **Rule #33: evaluate on data newer than the training data.** Expect some drop in performance, but not a severe one.

The common thread is to make training and serving read from the same definitions and, where you can, to train on what serving actually saw. A feature store gives you shared definitions for both paths. [1]

## Measure it: Rule #37

The guide asks you to measure skew at three points. [13]

1. **Training data versus holdout data.** The holdout is drawn from the same period as training, so the gap measures overfitting.
2. **Holdout data versus next-day data.** The next-day data was not seen in training. A drop here is expected to be small, since the world moves on a little.
3. **Next-day data versus live serving.** The gap here usually signals an engineering error, because it compares the same period scored by the training pipeline and by the live system.

If the first two gaps are small and the third is large, the model is fine and the plumbing is not. The practical output is a number you chart and alert on, not a one-off check.

:::low-confidence
The three measurement points and the point that a next-day versus live gap signals an engineering error come from the rule's text as read for this course. The explanations of the first two gaps (overfitting, and the world moving on) are the usual interpretation and were not confirmed word for word against the rule; check Rule #37 before quoting them. [13]
:::

## An example of the cause

Suppose training computes a user's account age with `(event - signup).dt.days`, and the serving code is a hand-written copy using `(now - signup).seconds // 86400`. In Python the `seconds` part of a time difference is only the remainder below one day, so the serving feature is wrong for anyone older than a day while every unit test of the model still passes. Rule #32 exists to make this kind of divergence impossible: one implementation used by both paths. The quiz uses this example.

:::key-takeaways
- Skew comes from different data handling in training and serving, data that changes between them, or feedback loops. [13]
- Log serving features, snapshot changing tables, reuse transformation code, and evaluate on newer data. [13]
- Measure skew at three points: training versus holdout, holdout versus next-day, next-day versus live. A large last gap points at engineering. [13]
:::

:::glossary
- **Training-serving skew**: the model does worse live than in training because the two paths handle data differently.
- **Serving**: running the model for real requests.
- **Feedback loop**: the model's output changes the data it later learns from.
- **Corpus**: the body of data something is trained or served on.
- **Sampling**: keeping only a portion of the data.
- **Importance weighting**: counting sampled examples more heavily so the sample still represents the whole.
- **Snapshot**: a frozen copy of a table at one moment.
- **Holdout data**: data from the training period that was kept out of training.
- **Overfitting**: learning the training data too exactly to handle new data.
- **Feature store**: a shared source of feature definitions for both paths.
- **Artifact**: the trained-model file handed from one team to another.
- **Divergence**: two copies of the same logic slowly becoming different.
:::
