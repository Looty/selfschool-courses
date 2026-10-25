---
id: l36
title: Retries, timeouts and failed tasks
quiz: quiz-04.yaml
resources: []
sources: [49, 51]
---
After this lesson you can read Airflow task states, configure retries and timeouts for a training task, and explain what a heartbeat timeout means.

## Operators, sensors and `@task`

Airflow tasks come in three forms: Operators (predefined templates), Sensors (a special operator that waits for an external event, such as a file or a table to appear) and `@task`-decorated Python functions. Calling an operator or sensor inside a Dag file creates a task. By default a task runs once all upstream tasks succeed. [51]

## Task states

The ideal path is `none`, `scheduled`, `queued`, `running`, `success`. Others include `failed`, `skipped`, `upstream_failed`, `up_for_retry`, `up_for_reschedule`, `deferred`, `awaiting_input` (human in the loop), `restarting` and `removed`. [51] `upstream_failed` is the one worth remembering when reading a red Dag: it names tasks that never ran because something before them failed, so the first failed task is the one to open, not the last red one.

## Retries

By default a failed task retries with a fixed count and delay. A retry policy can map exceptions to the actions RETRY, FAIL or DEFAULT; rules are checked in order and the first match wins. Policies run in the worker, cannot exceed `retries` and never apply to `AirflowFailException`. [51]

Two exceptions give a task explicit control: `AirflowSkipException` skips the task and `AirflowFailException` fails it with no remaining retries. [51] That distinction fits ML jobs. A bad credential or a failed data validation will fail the same way every time, so retrying wastes a GPU hour; fail fast. A preempted node or a flaky network call may succeed next time, so retry.

## Timeouts

`execution_timeout` limits each execution; a breach raises `AirflowTaskTimeout`, which can be retried. A sensor's `timeout` limits the total time until success in reschedule mode and raises `AirflowSensorTimeout`, which does not retry, and retries do not reset it. [51] A training task with no execution timeout can hang for as long as the cluster lets it; set one to a sensible multiple of the normal duration.

## Sensor modes

In reschedule mode a sensor runs periodically and frees its worker slot between checks. The page also mentions the `deferred` state and a separate guide on deferring, but does not explain deferrable or poke mode. [51]

## Zombies, now heartbeat timeouts

A task that still shows `running` after its worker has died is called a heartbeat timeout (formerly a "zombie"). Workers send regular "I'm alive" signals; when they stop, Airflow knows something went wrong. Typical causes are an out-of-memory kill (the system terminating a process that used too much memory), a failed liveness probe (Kubernetes health check) or a node move. Airflow periodically detects these and marks them failed or retries them. [51] On Kubernetes with large models, out-of-memory kills are a realistic source, so a retry that gives the task the same memory limit will fail again; fix the limit as well as the retry count.

## SLAs

SLAs were removed in Airflow 3.0 and replaced in 3.1 by Deadline Alerts, which the page links to but does not explain. [51] The Dags page also defers its coverage of deadlines to another page. [49] If your runbook relies on an SLA miss alert, check the current documentation.

:::low-confidence
Retry count and delay defaults, sensor poke and deferrable details, and Deadline Alerts are not explained by the pages used here. [51]
:::

:::key-takeaways
- Tasks are operators, sensors or `@task` functions; by default a task needs all upstream tasks to succeed. [51]
- `AirflowFailException` fails without retries; `AirflowSkipException` skips; use them to separate "will fail again" from "worth retrying". [51]
- `execution_timeout` bounds one execution and can be retried; a sensor timeout is not retried. [51]
- A task stuck in `running` after its worker dies is a heartbeat timeout; Airflow detects it and fails or retries it. [51]
:::

:::glossary
- **Operator / Sensor / `@task`**: a ready-made task type / a task that waits for an outside event / a plain Python function turned into a task.
- **Task state**: where a task is in its life (queued, running, success, failed, ...).
- **`upstream_failed`**: the task never ran because something before it failed.
- **`up_for_retry`**: failed, but waiting to be tried again.
- **Retry policy**: rules for when and how many times to try again.
- **Fail fast**: stop at once when retrying cannot help.
- **`AirflowFailException` / `AirflowSkipException`**: exceptions that force "fail with no retries" or "skip".
- **Preempted node**: a cloud machine taken away by the provider mid-job.
- **Timeout**: a time limit after which something is stopped.
- **`execution_timeout`**: the longest one run of a task may take.
- **Reschedule mode**: a sensor checks, then frees its worker until the next check.
- **Deferred**: handed to a helper that waits cheaply.
- **Heartbeat timeout (zombie)**: a task whose worker vanished without reporting.
- **OOM kill (out-of-memory)**: the system terminating a process that used too much memory.
- **Liveness probe**: a health check Kubernetes runs on a container.
- **SLA**: a promised deadline or service level.
- **Deadline Alerts**: Airflow 3.1's replacement for SLAs.
:::
