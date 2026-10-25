---
id: l34
title: Writing a Dag for an ML job
quiz: quiz-02.yaml
resources: []
sources: [49]
---
After this lesson you can declare a Dag, order its tasks, explain a run's logical date, and use branching and trigger rules without surprising skips.

## Declaring a Dag

The Dags page shows three ways to declare one: a `with DAG(...)` context manager that adds tasks inside the block automatically, the `DAG()` constructor with `dag=` passed to each operator, and the `@dag` decorator that turns a function into a Dag generator. [49]

```python
with DAG(
    dag_id="my_dag_name",
    start_date=datetime.datetime(2021, 1, 1),
    schedule="@daily",
):
    EmptyOperator(task_id="task")
```

The `schedule` argument accepts presets such as `"@daily"` and `"@once"`, cron strings and `"@continuous"`. A schedule is optional: Dags "do not require a schedule." [49]

## Ordering tasks

The recommended syntax is `>>` and `<<`; `set_upstream` and `set_downstream` are the explicit alternatives. `cross_downstream` links two lists fully and `chain` links tasks in sequence or pairwise. [49]

```python
first_task >> [second_task, third_task]
third_task << fourth_task
```

For an ML job this reads naturally: extract >> validate >> train >> evaluate >> register, with a fan-out where independent steps can run in parallel (for example, several models trained on the same prepared data).

## Runs and the logical date

Each run of a Dag creates a Dag Run, and runs can execute in parallel. Each run covers a data interval, the slice of time whose data it should process (for a daily Dag, yesterday). The logical date is a label for that run: for a manual run it is the trigger time; for a scheduled run it marks the start of the data interval, so a run that processes Monday's data actually starts on Tuesday. Backfills run copies of a Dag for past intervals. [49]

This matters for training. A nightly retraining Dag should select its data by the run's interval, not by "now", so a rerun or a backfill produces the same dataset it would have produced the first time. That is the reproducibility idea of lesson 8 applied to scheduling. The Dags page itself does not discuss idempotency, so treat this as design advice and not as a documented guarantee. [49]

## Trigger rules

By default a task runs when all its upstream tasks succeed; that is the `all_success` trigger rule. Other rules include `all_failed`, `all_done`, `one_success`, `none_failed`, `none_skipped` and `always`. [49] A cleanup or notification task usually needs a different rule from the default; `all_done` runs after upstream tasks finish whatever their result.

## Branching

A `@task.branch` function returns the id of a directly downstream task, a list of ids, or `None`. The chosen paths run and the others are skipped. [49] In an ML Dag this is where a model-validation step decides between "register and continue" and "stop here".

The page warns about a trap: do not use `all_success` or `all_failed` on a task downstream of a branch, because the skips cascade. It recommends `none_failed_min_one_success` for the join task after a branch. [49]

## Gaps in the page

The Dags page does not explain `catchup`, which appears only as `catchup=False` in example code, and several of its snippets are partial. Read the scheduling documentation before depending on backfill behaviour. [49]

:::low-confidence
Catchup, idempotent task design and retry safety are not covered by the page used here. Treat the "select data by the run's interval" advice above as an engineering convention. [49]
:::

:::key-takeaways
- Declare a Dag with `with DAG(...)`, the constructor or `@dag`; order tasks with `>>`. [49]
- A scheduled run's logical date marks the start of its data interval; select data by interval so reruns match. [49]
- The default trigger rule is `all_success`; use `all_done` for cleanup and `none_failed_min_one_success` to join after a branch. [49]
:::

:::glossary
- **Dag**: a workflow: tasks with one-way dependencies.
- **Operator**: a ready-made type of task (run a script, call a service, ...).
- **`EmptyOperator`**: a task that does nothing; a placeholder.
- **Context manager (`with`)**: Python syntax that sets something up for a block of code and tears it down afterwards.
- **Decorator (`@dag`, `@task`)**: a marker above a function that wraps it with extra behaviour.
- **Cron string**: a compact schedule like `0 3 * * *` (every day at 03:00).
- **`@daily` / `@once`**: schedule shortcuts.
- **Upstream / downstream**: earlier in the flow / later in the flow.
- **Fan-out**: one task followed by several that can run in parallel.
- **Dag Run**: one execution of a Dag.
- **Data interval**: the time slice of data a run is responsible for.
- **Logical date**: the label marking which interval a run belongs to.
- **Backfill**: running a Dag for past intervals you missed or want to redo.
- **Catchup**: whether Airflow automatically runs missed past intervals.
- **Idempotent**: running it twice gives the same result as running it once.
- **Trigger rule**: when a task is allowed to start, given how upstream tasks ended.
- **Branching**: choosing which path of tasks to follow; the others are skipped.
- **Skip cascade**: skipped tasks causing everything after them to be skipped too.
:::
