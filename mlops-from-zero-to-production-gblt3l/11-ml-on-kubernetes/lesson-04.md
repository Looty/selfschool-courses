---
id: l44
title: Ray on Kubernetes with KubeRay
quiz: quiz-04.yaml
resources: []
sources: [57, 59, 60]
---
After this lesson you can describe how KubeRay runs Ray clusters and jobs on Kubernetes, choose between a long-lived cluster and a per-job one, and avoid leaving idle GPUs behind.

## What KubeRay is

Ray is a tool for spreading Python work across many machines. KubeRay is described as the recommended way to run Ray on Kubernetes. It is a Kubernetes operator (a program that manages a particular kind of application for you) that runs Ray clusters natively, with each Ray node as a Pod: one head Pod that coordinates and many worker Pods that do the work. [59] Ray is the distributed Python runtime many teams use for large-scale training, tuning and batch inference; this lesson is about operating it, not about Ray's APIs.

KubeRay adds three custom resources: RayCluster, RayJob and RayService. The overview names them without explaining each. [59] The RayJob quickstart explains one of them.

Other points from the overview: optional autoscaling lets the operator add and remove Pods to match a workload; the operator supports heterogeneous compute nodes, including GPUs; and several Ray clusters with different Ray versions can run in one Kubernetes cluster. The page gives no configuration for autoscaling or GPUs, and it also promotes a commercial managed service. [59]

## RayCluster and RayJob

A RayCluster manages the Ray Pods. A RayJob "manages a Ray cluster and the job that runs on it": KubeRay creates a RayCluster and submits a job when the cluster is ready. A RayJob can build the cluster from `rayClusterSpec` or reuse an existing one through `clusterSelector`. [60]

By default (`K8sJobMode`) the operator creates a submitter Kubernetes Job that runs `ray job submit` against the cluster. Other submission modes are `HTTPMode`, `InteractiveMode` (alpha) and `SidecarMode`. Status fields report the result, for example `jobStatus: SUCCEEDED` and `jobDeploymentStatus: Complete`. [60]

This is the same Job idea as lesson 42, one level up: a Kubernetes Job submits work to Ray, and Ray distributes it across the worker Pods.

## Clean-up is not automatic

By default `shutdownAfterJobFinishes` is false, so the RayCluster and the submitter remain after the job finishes. When it is true, the operator deletes the RayCluster after the job ends, after the delay set by `ttlSecondsAfterFinished` (default 0, applicable only when shutdown is on). The submitter Job is kept because it holds the logs and is removed with the RayJob. [60]

For ML this is the line that matters for cost. A RayJob that leaves its cluster running holds its worker Pods, and any GPUs they requested, until someone deletes it. Set `shutdownAfterJobFinishes` for batch work and keep long-lived RayClusters for interactive use, where you accept the idle cost deliberately.

## With a queue in front

Kueue lists RayJob and RayCluster among its supported job types. [57] The RayJob page adds a warning: Kueue can modify the `suspend` field, so do not set it manually when using Kueue. [60] Combined, quota and fair sharing from lesson 43 apply to Ray workloads, and a GPU team can be limited by ClusterQueue instead of by who submits first.

## Version warnings

The RayJob page requires KubeRay v0.6.0 or later and recommends v1.1.1 or later with Ray 2.8.0 or later. Some features are alpha (for example `SidecarSubmitterRestart`) or deprecated (legacy `onSuccess` and `onFailure` deletion policies), and rules-based deletion cannot be combined with `shutdownAfterJobFinishes`. [60] The page also contradicts itself on a removal version, so check your version's docs before using a deletion option.

:::low-confidence
The overview does not explain RayService, autoscaling configuration or GPU setup, and the RayJob manifests are not shown in full. Do not infer details from the names. [59][60]
:::

:::key-takeaways
- KubeRay is an operator that runs each Ray node as a Pod: one head, many workers. [59]
- A RayJob creates a RayCluster, submits the job and, by default, leaves the cluster running afterwards. [60]
- Set `shutdownAfterJobFinishes` (with a TTL) for batch work to release GPUs. [60]
- Kueue supports RayJob; do not set `suspend` manually when Kueue manages it. [57][60]
:::

:::glossary
- **Ray**: a framework for running Python code in parallel across a cluster; used for training, tuning and batch inference.
- **KubeRay**: the operator that runs Ray on Kubernetes.
- **Operator**: a program that automates running a complex application on Kubernetes.
- **Custom resource**: a new kind of object added to Kubernetes, like `RayCluster`.
- **RayCluster / RayJob / RayService**: a Ray cluster / a cluster plus a job to run on it / a long-running Ray-based service.
- **Head Pod / worker Pod**: the coordinator and the machines that do the work.
- **Autoscaling**: adding or removing workers to match load.
- **Heterogeneous compute**: a mix of different machine types, such as CPU and GPU nodes.
- **Distributed training**: training one model across several machines at once.
- **Batch inference**: running predictions over a big dataset in one go.
- **Submitter Job**: the Kubernetes Job that hands the work to Ray.
- **`clusterSelector`**: reuse an existing cluster instead of creating one.
- **`shutdownAfterJobFinishes`**: delete the cluster when the job ends.
- **TTL (`ttlSecondsAfterFinished`)**: how long to wait before cleaning up.
- **Idle cost**: paying for GPUs that are reserved but doing nothing.
- **Kueue**: the job-queue add-on from the previous lesson.
- **Sidecar**: a helper container running next to the main one.
- **Alpha / deprecated**: experimental / being phased out.
:::
