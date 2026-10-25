---
id: l27
title: Monitoring without labels, and feedback loops
quiz: quiz-03.yaml
resources: []
sources: [1, 2, 14, 44]
---
After this lesson you can tell data drift from concept drift, use proxy signals while labels are delayed, and recognise a feedback loop in monitoring data.

## Two kinds of drift

Evidently's guide separates two things that are often confused. [44]

- **Data drift** (feature drift) is a change in what the incoming data looks like, for example customers getting older on average.
- **Concept drift** is a change in the rule connecting inputs to the answer (the model's "target"). The inputs may look the same, but what they mean has changed. The model keeps predicting from what it learned in training, so its accuracy can fall unless it is retrained.

The two often occur together, and practitioners use the terms interchangeably, but they can come apart. The guide's credit-scoring example shows concept drift without data drift: applicant characteristics stay the same while the risk of default changes with the macro environment. [44]

It describes three shapes of concept drift: gradual (slow change in patterns, "almost an in-built property" of ML models), sudden (an abrupt shift such as a new competitor) and recurring (cyclical, such as seasonality, which can often be modelled directly). [44]

## The label problem

The only direct measure of model quality is comparing predictions with real outcomes. In many systems outcomes arrive late: a loan defaults months later; a recommendation's value shows up in later behaviour. Until labels arrive you are blind on quality, and Google's guide lists performance degradation and data distribution changes as triggers for retraining, both of which depend on monitoring signals. [1]

## Proxy signals

When ground truth is missing, Evidently's guide recommends proxies. [44]

- **Prediction drift**: compare the distribution of model outputs across periods, such as predicted classes or probabilities, with tests like Kolmogorov-Smirnov or chi-squared, distance metrics like PSI or simple rules.
- **Input data drift**: monitor feature distributions, often by tracking the share of drifted features rather than every column alone.
- **Feature-target relationship**: watch correlations between features and predictions, which works best with interpretable features and smaller datasets.
- **Domain heuristics**: for example a falling click share on a recommendation block, or new product categories appearing in forecast inputs.

The technical-debt paper adds a classical check: the distribution of predicted labels should match the distribution of observed labels (prediction bias). It is necessary but not sufficient, since a null model can pass it, so slice it and combine it with other signals. [2]

All of these tell you something changed. None replaces labels. Plan for the labels: log the inputs and the model's output with an identifier you can join to the outcome later, so you can compute real quality when it arrives (lesson 25).

## Feedback loops in monitoring data

If the model's decisions affect what data you later see, monitoring data can mislead. The paper warns that a model can influence its own future training data, directly or through hidden loops between systems. [2] A model that only approves loans only observes outcomes for loans it approved, so its quality estimate is biased by its own behaviour. Randomisation or isolating part of the data from the model's influence helps. [2] Plan for this when you design what to log.

:::low-confidence
The Evidently page is a vendor guide, and it does not discuss incremental drift. Other sources may use different names for the drift shapes. [44]
:::

:::key-takeaways
- Data drift is a change in input distributions; concept drift is a change in the input-output relationship. [44]
- Without labels use proxies: prediction drift, input drift, feature-target relationships and domain heuristics. [44]
- Log inputs and outputs with identifiers so labels can be joined later. [14]
- A model's decisions can shape its own data; randomise or isolate part of the data. [2]
:::

:::glossary
- **Data drift / feature drift**: the inputs change.
- **Concept drift**: the relationship between inputs and the right answer changes.
- **Target**: the thing the model predicts.
- **Ground truth**: the real, confirmed outcome.
- **Delayed labels**: outcomes that only become known long after the prediction.
- **Proxy signal**: an indirect clue that something changed, used when the real answer is not yet known.
- **Prediction drift**: the model's outputs changing in distribution over time.
- **Probability**: the model's confidence as a number between 0 and 1.
- **PSI**: a score for how much a distribution has shifted.
- **Feature-target relationship**: how strongly an input moves with the answer.
- **Interpretable features**: inputs whose meaning is easy to understand.
- **Domain heuristic**: a business-specific sign of trouble, such as clicks falling.
- **Prediction bias**: predicted answers skewed compared with real outcomes.
- **Null model**: a model that ignores its input.
- **Feedback loop**: the model's decisions shape the data it later sees.
- **Seasonality**: patterns that repeat on a calendar cycle.
- **Identifier (ID) join**: logging an ID so a prediction can be matched to its outcome later.
:::
