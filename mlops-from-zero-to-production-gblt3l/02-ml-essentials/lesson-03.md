---
id: l07
title: Baselines, and launching without ML
quiz: quiz-03.yaml
resources: []
sources: [1, 13]
---
After this lesson you can explain why the first deliverable should be infrastructure and a simple baseline, and use a baseline to judge a model.

## Rule 1: you may not need ML yet

Google's "Rules of Machine Learning" starts with Rule #1: don't be afraid to launch a product without machine learning. Start with heuristics (simple hand-written rules of thumb), and adopt ML once you have data. [13] For an engineer this is familiar advice: ship the simplest thing that could work, and let measurement tell you whether something better is worth the cost.

## Rule 4: simple model, right infrastructure

Rule #4 says to keep the first model simple and get the infrastructure right. The first version should get examples to the learner, serve the model, and confirm that features arrive consistently in both training and serving. The simple model then acts as a baseline. [13]

This ordering is the whole premise of MLOps. A complicated model on shaky plumbing is hard to debug, because any failure could be the model, the data or the pipeline. A simple model on solid plumbing isolates the pipeline problems first. The infrastructure you build for the baseline, data in, features, serving and monitoring, is what every later model reuses.

## Baselines in the lifecycle

The lifecycle from lesson 3 has a validation step: confirm the model is adequate for deployment, meaning its predictive performance is better than a baseline. [1] A baseline can be a heuristic, a previous model or a deliberately simple model. Without one, a metric such as "0.91" has no meaning. In Google's offline model validation, a new model is also compared against the current production model and checked for consistency across segments of the data. [1]

## Practical consequences

- **Write the baseline down.** Record which baseline a model is compared with and the metrics it must beat. A promotion rule that says "better than the baseline on the agreed metrics" can be automated later.
- **Keep the pipeline, not only the model.** If the first model is replaced, the data extraction, preparation and serving code remain. Treat them as the product.
- **Know when ML is not paying for itself.** If a heuristic meets the need, the operational cost of a model, retraining, monitoring and incident response, may not be worth it. This is Rule #1 applied.

:::key-takeaways
- Rule #1: don't be afraid to launch without ML; start with heuristics. [13]
- Rule #4: keep the first model simple and get the infrastructure right; the simple model is the baseline. [13]
- Model validation means beating a baseline; offline validation also compares against the production model and checks segments. [1]
:::

:::glossary
- **Heuristic**: a simple rule of thumb, like "recommend whatever is most popular".
- **Baseline**: the simple thing a model must beat to be worth shipping.
- **Infrastructure**: the plumbing around the model: data in, features, serving, monitoring.
- **Learner**: Google's word for the training system that produces the model.
- **Features**: the inputs the model looks at.
- **Serving**: running the model so others can use it.
- **Offline validation**: checking a model on saved data before it touches real users.
- **Segment**: a subgroup of data, such as one country or device type.
- **Promotion rule**: the agreed condition a model must meet to go live.
- **Operational cost**: the ongoing work of keeping something running (retraining, monitoring, incidents).
:::
