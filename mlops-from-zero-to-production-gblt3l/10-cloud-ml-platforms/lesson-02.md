---
id: l38
title: Caching and reuse in managed pipelines
quiz: quiz-02.yaml
resources: []
sources: [37, 53]
---
After this lesson you can explain how SageMaker step caching decides to reuse a result, compare it with DVC's rules for re-running stages, and avoid stale-cache surprises.

## Why cache

Training and processing steps are expensive, in time and in cloud bills. Caching means remembering a result so you do not redo the same work: rerunning a pipeline after changing only the last step should not repeat the first four. Step caching "reuses the output of a previous successful run of a step (instead of recomputing it) when the step has the same configuration and inputs", which saves time and resources and gives consistent results across reruns with identical parameters. [53]

## How SageMaker decides

With step signature caching, Pipelines looks for a previous run of the current pipeline step with the same values for certain attributes; if it finds one, it propagates the earlier outputs instead of recomputing. The attributes checked depend on the step type. [53] The page lists them on a separate page that was not read here, so this lesson cannot say what, for instance, the training step compares.

The rules that the page does state:

- **Opt in.** Caching is off by default.
- **A timeout is required.** It defines how old a previous run may be and still be a candidate for reuse.
- **Successful runs only.** A failed run is never reused. If several successful runs exist within the timeout, the most recent is used. If none match, the step reruns.
- **In progress.** If a matching run is still running, both steps continue and update the cache if they succeed.
- **Scope.** Caching is scoped to a single pipeline: a step from another pipeline cannot be reused, even if its signature matches.
- **Step types.** Processing, Training, Tuning, AutoML, Transform, ClarifyCheck, QualityCheck and EMR support it. [53]

## The same idea in DVC

Lesson 17 described the open-source version. DVC hashes the contents of a stage's dependencies and compares them to the previous run; if a dependency changed, the stage is invalidated and downstream stages that consume its outputs can be reproduced too. For parameters it only invalidates when the specific keys the stage lists have changed. `dvc repro --force` re-runs even when nothing changed. [37]

| | DVC stage | SageMaker step caching |
| --- | --- | --- |
| Reuse decided by | Hashes of dependencies and listed parameters [37] | Matching step-type attributes within a timeout [53] |
| Default | Always on for unchanged stages [37] | Off; must opt in [53] |
| Expiry | None described on the page read | Timeout you set [53] |
| Force a rerun | `--force` [37] | Turn caching off [53] |
| Scope | The repository's pipeline | One pipeline only [53] |

The "turn caching off" row comes from the page's existence of a separate topic for it, listed in the table of contents; the procedure was not read. [53]

## Stale-cache risks

A cache is only as good as its key. The biggest risk in either system is an input that changes without being part of the key: a table that was updated in place, a query that reads "latest", a file that is read inside the script but is not declared as a dependency. DVC's model of declaring deps explicitly (lesson 17) guards against some of it. For a managed step, the practical defences are the ones from earlier lessons: version the data (lesson 9), pass versioned references as step inputs, and set a timeout short enough that a stale result ages out.

:::low-confidence
The page lists which attributes make a cache key per step type only on another page, and it does not discuss cache invalidation when the data behind an unchanged S3 path changes. Check the cache-key page and test with a changed file before relying on it. [53]
:::

:::key-takeaways
- Step caching reuses a prior successful run with the same configuration and inputs; it is opt-in and needs a timeout. [53]
- Failed runs are never reused, and caching is scoped to one pipeline. [53]
- DVC reuses by hashing declared dependencies and listed parameters; both fail if an input is not part of the key. [37][53]
:::

:::glossary
- **Caching**: saving a result so identical work is not repeated.
- **Step caching**: SageMaker reusing a previous step result when the setup is the same.
- **Cache key / signature**: the set of values compared to decide "is this the same job as before?".
- **Opt in**: off unless you switch it on.
- **Timeout (cache)**: how old a saved result may be and still be reused.
- **Stale cache**: a reused result that is out of date because something changed that the key did not notice.
- **Invalidate**: mark a saved result as no longer usable.
- **Propagate outputs**: hand the saved outputs to the next steps.
- **Processing / Training / Tuning / AutoML / Transform**: SageMaker step types for data work, training, trying settings, automatic modelling and batch predictions.
- **EMR**: Amazon's managed service for big-data jobs.
- **ClarifyCheck / QualityCheck**: bias and data-quality check steps.
- **DVC stage**: one step of a DVC pipeline, re-run only when its inputs change.
- **Hash**: a fingerprint of contents.
- **`--force`**: DVC option to re-run regardless.
- **S3 path**: a location in Amazon's file storage.
:::
