---
id: l17
title: ML pipelines as DAGs
quiz: quiz-01.yaml
resources: []
sources: [1, 6, 20, 34, 35, 36, 37]
---
After this lesson you can describe an ML pipeline as a graph of steps, read a `dvc.yaml`, and compare a file-based pipeline (DVC) with a container-based one (Kubeflow Pipelines).

## A pipeline is a graph

An ML pipeline turns raw data into a model through ordered steps that each have inputs and outputs. Both tools in this lesson model it as a directed acyclic graph (DAG): a flowchart whose arrows only go forward and never loop back. Steps are the boxes, and a step that uses another's output must wait for it. [6][36]

## DVC: stages in a file

DVC defines pipelines in `dvc.yaml` as named stages. Each stage has a `cmd`, its `deps` (inputs), `params` (values read from a parameters file) and `outs` (outputs); metrics and plots can be declared too. DVC builds the graph from dependencies and outputs, so the order stages run in follows the graph, not the order in the file, and the graph must not contain cycles. [6]

```yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps: [src/prepare.py, data/raw]
    outs: [data/clean.csv]
  train:
    cmd: python src/train.py
    deps: [src/train.py, data/clean.csv]
    params: [learning_rate, nn.epochs]
    outs: [models/model.pkl]
    metrics:
      - metrics.json:
          cache: false
```

The key behaviour is **what re-runs**. DVC takes a fingerprint (hash) of each input's contents and compares it to the last run; if an input changed, that stage is out of date, and the stages after it that use its outputs get re-run too. For parameters it only invalidates a stage when the specific keys that stage lists have changed. Outputs are cached automatically. [6]

`dvc repro` regenerates the results: it restores the graph from `dvc.yaml`, checks which stages need to run and executes their commands in order. The documentation compares it to `make`, with the difference that DVC records stage dependencies and caches outputs. `--force` re-runs even when nothing changed, `--single-item` runs only the named stage, and `--pull` downloads missing data first; without `--pull`, `dvc repro` does not run `dvc checkout` or `dvc pull`. [37]

## Kubeflow Pipelines: components in containers

Kubeflow Pipelines (KFP) is described as a platform for building and deploying portable and scalable ML workflows that run in containers on Kubernetes-based systems. You write components and pipelines with the Python SDK, compile the pipeline to an intermediate representation in YAML, and submit it to a KFP-conformant backend, such as the open-source KFP backend or Google Cloud Vertex AI Pipelines. Each component execution corresponds to a single container execution. [20]

A component is a remote function definition with inputs, logic and outputs; instantiating it creates a task. [34] A lightweight Python component is a decorated function: [35]

```python
from kfp import dsl

@dsl.component
def add(a: int, b: int) -> int:
    return a + b
```

Inputs and outputs need type annotations. The function must be hermetic: it may not reference symbols defined outside its body, so imports and constants go inside it. The documentation notes this can be constraining for real code, and recommends containerized Python components when you need `packages_to_install`, to avoid installing dependencies at runtime. [35]

You compose components into a pipeline: [36]

```python
@dsl.pipeline
def pythagorean(a: float, b: float) -> float:
    a_sq_task = square(x=a)
    b_sq_task = square(x=b)
    sum_task = add(x=a_sq_task.output, y=b_sq_task.output)
    return square_root(x=sum_task.output).output
```

Tasks that do not exchange data run in parallel, and a task that consumes another's output waits for it. `.after()` forces an order without passing data. [36]

## Choosing

| | DVC pipelines | Kubeflow Pipelines |
| --- | --- | --- |
| Unit of work | A shell command in a stage | A component, one container per execution |
| Defined in | `dvc.yaml` in the repository | Python SDK, compiled to YAML |
| Skips unchanged work | Yes, by comparing hashes of deps and params | Not covered by the pages read for this course |
| Runs on | Your machine or a CI runner | A KFP backend on Kubernetes |

[6][20] They are not exclusive. The point of both is the same: a pipeline is code, versioned, and runnable the same way in development and in production, which is Level 1's "experimental-operational symmetry". [1]

:::low-confidence
The pages read for KFP cover defining components and pipelines but not compiling and running them, so this lesson does not show the compile and submit calls. Check the "Compile a Pipeline" and "Run a Pipeline" guides. [36]
:::

:::key-takeaways
- Both DVC and KFP model a pipeline as a DAG; a step that consumes another's output depends on it. [6][36]
- DVC re-runs a stage when the hash of a dependency or a listed parameter changes; `dvc repro` runs what is needed. [6][37]
- A KFP component runs in one container; components are composed into a pipeline compiled to YAML for a backend. [20][35][36]
:::

:::glossary
- **Pipeline**: automated steps where each step's output feeds the next.
- **DAG (directed acyclic graph)**: steps with one-way dependencies and no loops.
- **Stage**: one named step in a DVC pipeline.
- **`dvc.yaml`**: the file where a DVC pipeline is defined.
- **Dependency (`deps`)**: an input a stage needs; if it changes, the stage re-runs.
- **`outs` / outputs**: files a stage produces.
- **`params`**: settings read from a parameters file; only the listed ones can trigger a re-run.
- **Cache**: saved outputs so unchanged work is skipped.
- **`dvc repro`**: reruns whatever is out of date, like `make`.
- **`make`**: an old build tool that rebuilds only what changed.
- **Kubeflow Pipelines (KFP)**: a system for running ML pipelines as containers on Kubernetes.
- **Container**: a packaged mini-environment (like Docker) that runs the same anywhere.
- **Kubernetes**: software that runs and manages containers across many machines.
- **Component**: one reusable step in KFP; each run is one container.
- **SDK**: a code library for building things with a tool.
- **Intermediate representation (IR)**: the tool-neutral YAML file a pipeline gets compiled into.
- **Backend**: the server that actually runs the pipeline.
- **Vertex AI Pipelines**: Google Cloud's managed service that runs KFP pipelines.
- **Hermetic**: self-contained; uses nothing from outside itself.
- **Experimental-operational symmetry**: the same pipeline runs in development and production.
:::
