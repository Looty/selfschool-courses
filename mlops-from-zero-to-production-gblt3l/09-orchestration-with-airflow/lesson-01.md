---
id: l33
title: Airflow architecture for ML workflows
quiz: quiz-01.yaml
resources: []
sources: [48]
---
After this lesson you can name the components of an Airflow deployment, trace a task from a Dag file to a worker, and say what a workflow scheduler adds next to the ML pipeline tools of chapter 5.

## A workflow is a Dag

Airflow is a platform for building and running workflows, meaning scheduled chains of jobs. A workflow is a Dag, a directed acyclic graph of tasks: a one-way flowchart where the arrows say "this must finish before that starts". The Dag "specifies the dependencies between tasks, which defines the order in which to execute the tasks." [48] This is the same idea as the DVC and Kubeflow graphs of lesson 17, applied one level up: a Dag is usually the thing that decides when pipelines, data loads, training jobs and reports run, and in what order.

## The components

Airflow 3 splits the system into parts, some required and some optional. [48]

- The **scheduler** triggers scheduled workflows and submits tasks to the executor. The executor is a configuration property of the scheduler and runs inside its process.
- The **Dag processor** parses Dag files from a Dag bundle and serializes them into the metadata database. It is required in every Airflow 3 deployment and always runs as a standalone process.
- The **Dag bundle** is the source location of Dag files. By default it is a local folder, and workers use it to get the right version of a Dag file.
- The **API server** serves the REST API and the user interface. Tasks also use it to report their state, so they do not need direct database access.
- The **metadata database**, usually PostgreSQL or MySQL, stores the state of tasks, Dags and variables.
- A **worker** executes the tasks the scheduler hands out. It can be a long-lived process (CeleryExecutor) or a pod (KubernetesExecutor). Workers are listed as optional.
- The **triggerer** runs deferred tasks in an asyncio event loop. Plugins extend Airflow and are read by several components.

## What happens to one task

The page describes the flow in order. [48]

1. Dag files are synced from the Dag bundle and parsed by the Dag processor, which stores the serialized Dags in the metadata database.
2. The scheduler reads the database, triggers runs on schedule and submits ready tasks to the executor.
3. A worker runs each task in its own subprocess, using the Dag bundle version the scheduler specified. Nothing is pooled or reused, so capacity must cover the peak number of concurrent task instances.
4. A task waits for its upstream tasks to succeed by default. Branching, LatestOnly and trigger rules change this.
5. Small values pass between tasks as XComs; large files go through external storage (lesson 35).
6. The UI shows run status, logs and the graph.

Only the worker holds short-lived credentials and talks to the Execution API, so task code never reaches the metadata database directly. [48]

## Deployment advice from the documentation

The page lists these recommendations. [48]

- Separate the Dag processor from the scheduler, for security isolation from Dag author code.
- Prefer a versioned Dag bundle backend such as Git. With local disk, the Dag processor and workers can briefly see different versions.
- Budget worker capacity for peak concurrent task instances.
- Use Pools to limit concurrency and Connections and Hooks to manage access to shared resources.
- For a small install, one machine with LocalExecutor is enough.

## Where it fits in an ML system

In this course's framing, not a claim of the Airflow page: DVC stages and Kubeflow components define the steps of one ML pipeline, while a scheduler decides when each pipeline runs, what must finish first (a fresh upstream table, for instance) and what happens when a step fails. That is the "triggers" part of Google's Level 1 automation from lessons 4 and 20. A team already running Airflow for data work often calls its ML jobs from the same Dags.

:::low-confidence
The architecture page gives no sizing numbers and no executor tuning advice, so this lesson cannot say how many workers a given ML workload needs. Test with your own task counts. [48]
:::

:::key-takeaways
- A Dag is a graph of tasks that defines execution order. [48]
- Required parts: scheduler, Dag processor, API server, metadata database. Workers and the triggerer are optional. [48]
- Tasks report state through the API server, not directly to the database. [48]
- Use a versioned Dag bundle such as Git and size workers for peak concurrency. [48]
:::

:::glossary
- **Orchestration**: coordinating when and in what order jobs run, and what to do when one fails.
- **Airflow**: a popular open-source workflow scheduler.
- **Dag**: a directed acyclic graph; Airflow's word for one workflow.
- **Task**: one unit of work in a Dag.
- **Scheduler**: the component that decides what should run now and hands tasks out.
- **Executor**: the mechanism that actually launches tasks (on this machine, on Celery workers, on Kubernetes).
- **Dag processor**: reads your Dag files and stores them in a form the scheduler can use.
- **Dag bundle**: the place Dag files come from, such as a folder or a Git repository.
- **API server**: serves Airflow's web UI and REST API.
- **Metadata database**: Airflow's own database that remembers what ran and how it went.
- **Worker**: a process that runs tasks.
- **Pod**: Kubernetes' smallest running unit (one or more containers).
- **Triggerer / deferred task**: a helper that waits on slow external events without tying up a worker.
- **asyncio event loop**: Python's way of waiting on many things at once.
- **Plugin**: an add-on that extends Airflow.
- **Subprocess**: a separate process started by another.
- **XCom**: a small message passed between tasks.
- **Trigger rule**: the condition under which a task starts, such as "all upstream tasks succeeded".
- **Pool / Connection / Hook**: a concurrency limit; saved login details for an outside system; code that uses a connection.
- **Idle capacity**: unused room; here, workers must cover the peak, since nothing is shared.
:::
