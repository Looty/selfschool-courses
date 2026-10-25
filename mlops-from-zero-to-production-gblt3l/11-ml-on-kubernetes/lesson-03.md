---
id: l43
title: Queues and quotas with Kueue
quiz: quiz-03.yaml
resources: []
sources: [56, 57, 58]
---
After this lesson you can explain what Kueue adds to Kubernetes, read a ClusterQueue, and predict how borrowing and preemption share GPUs between teams.

## The problem

Kubernetes will happily create Pods for ten teams' training Jobs at once and leave most of them stuck waiting (Pending). Nothing in a plain Job decides who waits, who goes first or how much each team may use. Kueue is a Kubernetes add-on that acts like a ticket queue with quotas: it decides when a job waits, when it is admitted to start and when it is preempted (kicked off to make room for others). [57]

It does not replace core components. Autoscaling, Pod scheduling and the job lifecycle stay with the cluster autoscaler, kube-scheduler and kube-controller-manager. [57] It works with the Job from lesson 42: Kueue holds a Job suspended until its quota is available (Job suspension deletes active Pods until resumed). [56][57]

## Supported workloads

The overview lists batch Jobs, Kubeflow training jobs, RayJob, RayCluster, JobSet and plain Pods among the supported types, with stable in-tree integrations including MPIJob, RayService and StatefulSet. It marks SparkApplication and TrainJob (Kubeflow Trainer v2) as alpha, and lists JAXJob, PaddleJob, PyTorchJob, TFJob and XGBoostJob (Kubeflow Trainer v1) as deprecated, advising migration to TrainJob or JobSet. [57] That deprecation note is worth checking against your Kubeflow version.

The overview does not define ClusterQueue, LocalQueue, ResourceFlavor and Workload; it links to other pages. [57] This lesson covers ClusterQueue, which a separate page does define.

## ClusterQueue: a pool with quotas

A ClusterQueue is a cluster-scoped object that governs a pool of resources such as pods, CPU, memory and accelerators. It defines quotas per resource flavor and fair-sharing rules across ClusterQueues, and only batch administrators should create them. [58]

```yaml
apiVersion: kueue.x-k8s.io/v1beta2
kind: ClusterQueue
metadata:
  name: "cluster-queue"
spec:
  namespaceSelector: {} # match all.
  resourceGroups:
  - coveredResources: ["cpu", "memory", "pods"]
    flavors:
    - name: "default-flavor"
      resources:
      - name: "cpu"
        nominalQuota: 9
      - name: "memory"
        nominalQuota: 36Gi
      - name: "pods"
        nominalQuota: 5
```

This admits workloads only while total CPU requests are at most 9, memory at most 36Gi and pods at most 5. [58]

**Flavors** are variations of a resource, for example GPU models, mapped to node groups through ResourceFlavor objects. At admission Kueue assigns the first flavor in the list with enough unused quota. [58] Listing a "spot" flavor before an "on-demand" one therefore prefers the cheaper capacity while it lasts.

The per-flavor quota fields are: [58]

- `nominalQuota`: the quantity available to the ClusterQueue.
- `borrowingLimit`: the most it can borrow from unused nominal quota of other ClusterQueues in its cohort.
- `lendingLimit`: the most it lets cohort peers borrow when it is not using its quota.

## Cohorts and borrowing

ClusterQueues sharing the same `.spec.cohort` can borrow each other's unused quota; one with no cohort cannot borrow. In the page's example, when `team-b-cq` has no admitted workloads, `team-a-cq` (nominal 9 CPUs) can admit up to 21 CPUs counting team B's 12. If `team-b-cq` has pending workloads and team A has used its nominal quota, Kueue admits team B's first, protecting its nominal quota. [58] Borrowing turns idle capacity into throughput without giving up each team's guarantee.

## Queueing strategy and preemption

`queueingStrategy` can be `StrictFIFO`, where an older workload that cannot be admitted blocks newer ones even if they would fit, or `BestEffortFIFO`, the default, where it does not. [58]

Preemption is set under `.spec.preemption`: `reclaimWithinCohort` (can a pending workload preempt cohort workloads that use more than their nominal quota), `borrowWithinCohort` and `withinClusterQueue`, with values such as `Never` (the default), `LowerPriority` and `Any`. [58] Preemption deletes active Pods (lesson 42), so a preemptible training job needs checkpoints, otherwise it restarts from zero.

:::low-confidence
The pages used do not explain LocalQueue, Workload or fair-sharing mechanics, and the preemption heuristics are on a separate page. The checkpoint advice is the course's, not Kueue's. [57][58]
:::

:::key-takeaways
- Kueue decides when jobs wait, are admitted or are preempted; scheduling and autoscaling stay with core Kubernetes. [57]
- A ClusterQueue sets `nominalQuota` per flavor; cohorts allow borrowing and lending within limits. [58]
- `BestEffortFIFO` is the default; `StrictFIFO` lets an older blocked workload hold up newer ones. [58]
- Preemption is configured per ClusterQueue and deletes Pods, so make preemptible jobs resumable. [57][58]
:::

:::glossary
- **Kueue**: a Kubernetes add-on that queues jobs and enforces resource quotas.
- **Quota**: the amount of resources a team or queue is allowed to use.
- **Admit**: let a waiting job start.
- **Preempt**: stop a running job to free resources for a more deserving one.
- **kube-scheduler**: the Kubernetes component that picks which node runs each Pod.
- **Cluster autoscaler**: adds or removes machines depending on demand.
- **Job suspension**: holding a Job paused (no Pods) until it may start.
- **Kubeflow / Ray / MPI / JobSet**: other systems and job types for distributed training that Kueue can queue.
- **Alpha / deprecated**: experimental / scheduled for removal.
- **ClusterQueue**: a pool of resources with quotas, set up by administrators.
- **LocalQueue**: the queue a team submits jobs to (it feeds a ClusterQueue).
- **ResourceFlavor**: a kind of resource, such as "A100 GPU nodes" or "spot machines".
- **Spot / on-demand**: cheap but revocable cloud machines / normal-price reliable ones.
- **`nominalQuota`**: the amount a queue is guaranteed.
- **Borrowing / lending**: using, or letting others use, spare quota.
- **Cohort**: a group of queues that can share spare quota.
- **FIFO (first in, first out)**: oldest first.
- **`StrictFIFO` / `BestEffortFIFO`**: an older stuck job blocks newer ones / newer ones may jump ahead.
- **Checkpoint**: saving training progress so a stopped job can resume rather than restart.
- **Namespace selector**: which parts of the cluster the queue serves.
:::
