---
id: l42
title: Training as Kubernetes Jobs
quiz: quiz-02.yaml
resources: []
sources: [55, 56]
---
After this lesson you can run a training task as a Kubernetes Job, choose between a single run, a fixed count and a work queue, and predict how failures are retried.

## A Job is a run-to-completion task

A Job represents a one-off task that runs to completion and then stops. It creates one or more Pods and keeps retrying until a specified number of them terminate successfully. If a Pod is deleted or fails, for example from a node hardware failure or a reboot, the Job starts a new one, and deleting the Job cleans up its Pods. [56] Compared with a Deployment (Kubernetes' object for services that should stay running forever), a Job is the right shape for work that has an end: training, evaluation and batch scoring.

The page's example computes pi in a container. The parts to copy: `restartPolicy: Never` and `backoffLimit: 4`. The Pod template's restart policy must be `Never` or `OnFailure`. [56]

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34.0
        command: ["perl",  "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```

For a training Job you would add the GPU in `resources.limits` as in lesson 41 and a node selector for the accelerator type. [55]

## Completions and parallelism

The page distinguishes three types. [56]

- **Non-parallel.** Normally one Pod, restarted only if it fails. With `completions` and `parallelism` both unset, both default to 1.
- **Fixed completion count.** Set `.spec.completions` to a positive number; the Job is complete when that many Pods have succeeded. `parallelism` controls how many run at once and defaults to 1.
- **Work queue.** Leave `completions` unset and set `parallelism`. When any Pod terminates with success, no new Pods are created. The Pods coordinate among themselves, for example by reading from an external queue.

A `parallelism` of 0 effectively pauses the Job. For fixed-count Jobs, the number running in parallel never exceeds the remaining completions. [56]

For ML, a fixed count suits "evaluate 8 shards of a dataset"; a single run suits one training task; a work queue suits many independent tasks, such as hyperparameter trials pulled from a shared list.

## Indexed Jobs

In `completionMode: Indexed` each Pod gets an index from 0 to `completions - 1`, exposed as an annotation, a label, a hostname pattern `$(job-name)-$(index)` and the environment variable `JOB_COMPLETION_INDEX`. [56] A script can read that variable to choose its shard of the data. More than one Pod can start for the same index, and only the first to succeed counts. [56] That means shard work must be safe to repeat, which is the idempotency habit from lessons 8 and 34.

```yaml
spec:
  parallelism: 8
  completions: 8
  completionMode: Indexed
```

## Failures and retries

`backoffLimit` defaults to 6 unless a per-index limit is specified. Retries are delayed with an exponential back-off (10s, 20s, 40s and so on), capped at ten minutes. A retry is counted for Pods in the `Failed` phase and, with `restartPolicy: OnFailure`, for container restarts in Pending or Running Pods. [56]

Two choices follow. With `restartPolicy: Never` a failed Pod stays for you to inspect and a fresh Pod is created; with `OnFailure` the container restarts in place. For a training job whose failure you want to debug, keeping the failed Pod's logs is usually easier. And as with Airflow retries (lesson 36), a failure that repeats, such as a bad dataset, burns retries and compute; a low `backoffLimit` limits the damage. [56]

## Suspend

Suspending a Job deletes its active Pods until it is resumed. [56] This is what lets a queueing system hold a Job until quota is available (lesson 43).

:::low-confidence
The sections on `ttlSecondsAfterFinished`, `activeDeadlineSeconds` and the pod failure policy were not read, so this lesson does not describe cleanup of finished Jobs, an overall deadline or exit-code-based retry rules. [56]
:::

:::key-takeaways
- A Job runs Pods to completion and replaces failed ones; restartPolicy must be `Never` or `OnFailure`. [56]
- Single run, fixed completion count and work queue are set by `completions` and `parallelism`. [56]
- Indexed mode gives each Pod `JOB_COMPLETION_INDEX`; duplicate Pods per index are possible, so make shards repeatable. [56]
- `backoffLimit` defaults to 6, with an exponential delay capped at ten minutes. [56]
:::

:::glossary
- **Job (Kubernetes)**: a task that runs until it succeeds, then stops.
- **Deployment**: a Kubernetes object for services meant to run continuously.
- **Pod**: Kubernetes' smallest running unit.
- **`restartPolicy`**: what happens when a container exits (`Never` or `OnFailure` for Jobs).
- **`backoffLimit`**: how many times to retry a failing Job before giving up.
- **Exponential back-off**: waiting twice as long before each retry (10s, 20s, 40s ...).
- **`completions` / `parallelism`**: how many Pods must succeed / how many run at the same time.
- **Work queue**: Pods pull tasks from a shared list until it is empty.
- **Indexed Job**: each Pod gets its own number, handy for splitting data into shards.
- **Shard**: one slice of a dataset or workload.
- **`JOB_COMPLETION_INDEX`**: the environment variable holding a Pod's number.
- **Idempotent**: safe to repeat; running twice equals running once.
- **Annotation**: extra notes attached to a Kubernetes object.
- **Suspend**: pause a Job by removing its running Pods.
- **Hyperparameter trial**: one attempt at training with one choice of settings.
- **Node hardware failure / reboot**: reasons a Pod may disappear.
- **Pod phase `Failed`**: a Pod ended with an error.
:::
