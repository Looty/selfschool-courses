---
id: l35
title: Passing data between tasks
quiz: quiz-03.yaml
resources: []
sources: [48, 50]
---
After this lesson you can use XComs correctly, say what must not go through them, and choose where large ML artifacts should live instead.

## Tasks are isolated

Airflow tasks are isolated by default and may run on different machines, so one task cannot just read another's variables. Each task runs in its own subprocess and nothing is reused. [48] To pass information between them, Airflow offers XComs ("cross-communications"): small notes left for later tasks. Each XCom is identified by a key, plus the `task_id` and `dag_id` it came from, and its value can be anything serializable (convertible to stored bytes, like JSON). [50]

## What XComs are for

The documentation is clear about the intent. XComs are for passing data within a Dag run, not for global configuration (Variables serve that). They are "only designed for small amounts of data", and the page advises against passing large values such as dataframes. [50]

Two more limits follow from the text. XComs are cleared when a task that failed earlier is retried, so they cannot hold state across retries or sensor pokes. And XCom operations should go through the task context, because the XCom database model cannot be updated directly. [50]

## Pushing and pulling

Values are pushed and pulled with `xcom_push` and `xcom_pull` on the task instance. [50]

```python
task_instance.xcom_push(key="identifier as a string", value=any_serializable_value)
task_instance.xcom_pull(key="identifier as string", task_ids="task-1")
```

Operators and `@task` functions push their return value automatically under the key `return_value` when `do_xcom_push` is enabled, which is the default, and `xcom_pull` uses that key when none is given. [50] To push several values, set `do_xcom_push` and `multiple_outputs` to `True` and return a dictionary; each key can then be pulled separately. [50]

One change catches migrating teams. In Airflow 3, `xcom_pull()` without `task_ids` pulls only from the current task, while Airflow 2 searched all tasks. Always name `task_ids` when pulling from another task. [50]

## What goes in an XCom in an ML Dag

Use the rule of "small and descriptive". Good candidates are a run identifier, a path or URI to a dataset, a model-registry version number, or a metric value used by a branch. Bad candidates are the dataset itself, the trained model file or a large evaluation table.

The mechanism for large data is storage outside Airflow: tasks write to object storage, a feature store or a model registry (lessons 11 and 14) and pass the location in an XCom. This also helps lineage, because the location is a stable reference you can record in the run's metadata (lesson 15). The architecture page makes the same split: XComs for small metadata, external storage for large files. [48]

## Backends

The default `BaseXCom` stores values in the Airflow database. That suits small values but can struggle with large values or high volume, and the documentation recommends object storage for bigger data, pointing to the common-io provider. [50] A custom backend is chosen with the `xcom_backend` configuration option: subclass `BaseXCom` and override `serialize_value` and `deserialize_value`, optionally `purge`. [50]

A custom backend moves the bytes, but does not change the design point. A model file still needs a registry for versioning, aliases and approval; storing it in an XCom backend gives you none of that.

:::low-confidence
The XCom page does not give a size threshold, so "small" is a judgement. A pragmatic limit is "metadata and references only", and no number is documented here. [50]
:::

:::key-takeaways
- XComs pass small values within a run; they are not configuration and not for dataframes. [50]
- A return value is pushed as `return_value` automatically; name `task_ids` when pulling in Airflow 3. [50]
- Pass references (paths, versions, run ids) through XComs and keep large artifacts in external storage. [48][50]
- A custom XCom backend changes where bytes live, not whether you need a model registry. [50]
:::

:::glossary
- **XCom**: "cross-communication"; a small value one task leaves for another.
- **Serializable**: can be converted to bytes or text for storing.
- **Variable (Airflow)**: a global setting shared by Dags.
- **Task instance**: one task within one Dag run.
- **`xcom_push` / `xcom_pull`**: save a value / fetch a value.
- **`return_value`**: the default key under which a task's return value is stored.
- **Dataframe**: a table of data held in memory (as in pandas).
- **Sensor poke**: a sensor's repeated check of whether the thing it waits for exists yet.
- **Object storage**: cloud file storage such as S3 for large files.
- **URI**: an address such as `s3://bucket/path/file`.
- **Lineage**: the trail of what data produced what.
- **XCom backend**: where XCom values are physically stored.
- **Subclass / override**: create a customised version of a class by changing some of its methods.
- **Migration (Airflow 2 to 3)**: upgrading to a new major version where some behaviour changed.
:::
