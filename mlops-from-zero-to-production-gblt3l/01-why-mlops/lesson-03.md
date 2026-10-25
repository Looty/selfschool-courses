---
id: l03
title: The ML lifecycle, from data to monitoring
quiz: quiz-03.yaml
resources: []
sources: [1, 14]
---
After this lesson you can name the steps of the ML lifecycle, say what each one produces, and explain how monitoring feeds the next iteration.

## Eight steps

If words like model, training or features are unfamiliar, read the "New to ML?" box in lesson 1 first. This lesson is a map; each step gets its own chapter later (steps 1 to 3 in chapter 3, steps 4 to 6 in chapters 2 and 4, step 7 in chapter 6, step 8 in chapter 7).

Google's guide breaks the data science work for building an ML model into these steps. Each can be done by hand or automated. [1]

1. **Data extraction.** Select and integrate the relevant data from different sources.
2. **Data analysis.** Exploratory data analysis (EDA): poke around in the data to learn its shape and quirks, and decide what cleaning and feature engineering (turning raw data into useful model inputs) it needs.
3. **Data preparation.** Clean the data, split it into a training set (to learn from), a validation set (to tune with) and a test set (for a final honest check), and transform it into model inputs. The output is the prepared splits.
4. **Model training.** Pick algorithms, try different settings (hyperparameter tuning), and produce a trained model.
5. **Model evaluation.** Score the model on a holdout test set, data it never saw, to get its quality numbers (metrics).
6. **Model validation.** Confirm that the model is adequate for deployment, meaning its predictive performance is better than a baseline.
7. **Model serving.** Deploy the validated model. The guide names three forms: a microservice with a REST API for online predictions, an embedded model on an edge or mobile device, or part of a batch prediction system.
8. **Model monitoring.** Watch the model's predictive performance to decide whether to start a new iteration.

Evaluation and validation are easy to confuse. Evaluation produces the metrics. Validation uses them, together with a baseline, to decide whether the model may ship. [1]

## A loop, not a line

Monitoring is not the end. In the CD4ML description, a model is built reproducibly, evaluated, productionized, tested, deployed and monitored, and then data from production flows back into new training datasets, which makes the whole thing a loop of continuous improvement. [14] The guide's pipeline triggers come from the same idea: a retrain can start on demand, on a schedule, when new training data arrives, when model performance degrades, or when the data distribution changes significantly. [1]

## What an operator owns

The work of MLOps is to make every arrow in the loop repeatable: how data gets in, how a model is produced, how it is judged, how it is served and how its behaviour in production gets back to the start. The rest of this course follows that order: data and features, experiments and models, pipelines, serving, monitoring.

:::key-takeaways
- Eight steps: data extraction, analysis, preparation, model training, evaluation, validation, serving, monitoring. [1]
- Evaluation produces metrics; validation decides whether the model beats a baseline and may ship. [1]
- Serving can be an online REST service, an embedded model, or a batch system. [1]
- Production monitoring feeds new training data and new iterations. [1][14]
:::

:::glossary
- **Lifecycle**: the stages something goes through from start to finish, here from raw data to a monitored model.
- **EDA (exploratory data analysis)**: looking through the data with charts and summaries before modelling.
- **Feature engineering**: turning raw data into inputs a model can learn from, like turning a date into "day of week".
- **Training / validation / test sets**: three separate chunks of data, used to learn, to tune, and for a final exam.
- **Holdout set**: data kept aside so the model is tested on things it has never seen.
- **Hyperparameter tuning**: trying different training settings to find the best ones.
- **Metric**: a number that scores how good the model is.
- **Baseline**: a simple reference to beat, such as the current model or "always guess the most common answer".
- **Serving**: running the model so other programs can ask it for predictions.
- **REST API**: a standard way for programs to talk over HTTP; here, "send input, get a prediction back".
- **Edge device**: a phone or small gadget that runs the model locally.
- **Batch prediction**: predicting for a big pile of records at once, on a schedule.
- **Productionize**: make something solid enough to run for real users.
:::
