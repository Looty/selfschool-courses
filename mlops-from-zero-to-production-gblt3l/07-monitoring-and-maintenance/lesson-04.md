---
id: l28
title: "Staleness, retraining and incident response"
quiz: quiz-04.yaml
resources: []
sources: [4, 13, 40, 43, 44]
---
After this lesson you can set how fresh a model must be, handle a degraded model without retraining, and run an ML incident with a rollback.

## How fresh must the model be?

Rule #8 of the Rules of ML says to know the freshness requirements of your system: measure how much performance degrades as the model ages. That sets how closely it needs watching and how often to retrain. [13] The method is concrete. Take an old model, score it on newer data and see how much performance drops per week, month or quarter. A model that loses little in a year does not need weekly retraining; one that loses a lot in a week needs automation and monitoring (lesson 20).

## Silent failures

Rule #10 is to watch for silent failures: things going wrong with no error message. For example, an upstream table that stops being refreshed (goes stale) can quietly degrade performance with nothing crashing. The guide's advice is to track statistics of the data and to inspect the data now and then. [13] Rule #11 asks you to give feature columns owners and documentation, so that when a feature breaks someone knows what it is and who to ask. [13]

## Before export: Rule #9

Rule #9 is to detect problems before exporting models: run sanity checks, such as performance on held-out data, before a model is exported. The guide suggests that problems with a model not yet shipped can be an email alert, while problems with a user-facing model may warrant a page. [13] This ties the lesson to your release gate (lesson 16).

## When retraining is not the answer

Evidently's guide lists options. Retraining is the most direct fix, with choices such as using only recent data, combining old and new data, or weighting recent examples more heavily. It needs new labelled data, and the guide cautions against training on unrepresentative periods such as a seasonal spike. New models should be tested before rollout and monitored afterwards. [44]

When retraining is not feasible, the guide lists process changes: adjusting decision thresholds, human-in-the-loop review for unusual or low-confidence cases, switching to alternative models or heuristics such as a "most popular items" fallback, pausing the model, or doing nothing for a while if the impact is tolerable. [44]

## An ML incident, step by step

An incident runbook for a degraded model borrows from ordinary SRE practice, with ML-specific steps.

1. **Detect and decide who is paged.** Page on user-visible symptoms; treat the rest as tickets (lesson 25). [43]
2. **Stop the damage.** If a recent release is the suspect, roll back. With a registry alias, rollback is moving the alias back to the previous version; with a KServe canary it is setting the canary share to zero. [4][40]
3. **Look at the layers.** Service health, then data (upstream freshness, schema, drift), then the model (predictions, quality metrics).
4. **Choose a remedy.** Fix the upstream data, retrain, adjust thresholds, fall back to a heuristic or pause the model. [44]
5. **Record and learn.** Add the check that would have caught it, such as a new data-validation rule or an alert, to the pipeline.

:::key-takeaways
- Measure how much performance decays as the model ages; that sets the retraining cadence (Rule #8). [13]
- Watch for silent failures and give features owners (Rules #10, #11). [13]
- Retraining is one remedy; thresholds, human review, fallbacks and pausing are others. [44]
- Roll back first when a release is suspected: move the alias or set the canary to zero. [4][40]
:::

:::glossary
- **Freshness**: how recent a model's training data needs to be to stay good.
- **Staleness**: a model or data source being out of date.
- **Silent failure**: a problem that produces no error, just worse results.
- **Upstream table**: data produced earlier in the chain that your model reads.
- **Feature column owner**: the person responsible for a specific input.
- **Sanity check**: a quick test that catches obviously broken results.
- **Held-out data**: data not used in training.
- **Decision threshold**: the cut-off score for "yes".
- **Human-in-the-loop**: a person reviews or decides the doubtful cases.
- **Fallback / heuristic**: a simple backup rule, such as "show the most popular items".
- **Labelled data**: examples with known correct answers.
- **Unrepresentative period**: a stretch of time (like a holiday spike) that is not typical.
- **Runbook**: a written step-by-step guide for handling a known kind of incident.
- **Incident**: an unplanned problem affecting users.
- **Alias / canary**: the registry pointer and the small-traffic rollout used for rollback.
- **SRE**: site reliability engineering, the discipline of keeping services dependable.
:::
