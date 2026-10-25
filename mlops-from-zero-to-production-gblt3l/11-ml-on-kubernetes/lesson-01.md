---
id: l41
title: GPUs on Kubernetes
quiz: quiz-01.yaml
resources: []
sources: [55]
---
After this lesson you can explain how a Pod gets a GPU, write the request correctly, and place Pods on the right GPU type.

## Device plugins

Kubernetes runs your containers inside Pods (the smallest unit it schedules) on machines called nodes. It manages AMD and NVIDIA GPUs (graphics chips that do the heavy maths for ML) across nodes through device plugins: small add-ons that tell Kubernetes "this node has GPUs". The feature has been stable since Kubernetes v1.26. [55] The administrator installs the vendor's GPU drivers on each node and then runs the vendor's device plugin. Once the plugin is running, the cluster exposes a custom schedulable resource such as `amd.com/gpu` or `nvidia.com/gpu`, and containers request it the same way they request `cpu` or `memory`. [55]

The division of labour matters for an operator. The page states that installing drivers and running the right device plugin on each node is the administrator's job, and that the linked vendor plugins and Node Feature Discovery are third-party projects whose authors the Kubernetes project is not responsible for. [55] If a GPU Pod stays Pending, an unready plugin or a missing driver is as likely a cause as a lack of capacity.

## Request them in limits

GPUs are meant to be specified in the `limits` section. [55]

- You can specify GPU `limits` without `requests`, because Kubernetes uses the limit as the request by default.
- You can specify both, but the values must be equal.
- You cannot specify GPU `requests` without `limits`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-vector-add
spec:
  restartPolicy: OnFailure
  containers:
    - name: example-vector-add
      image: "registry.example/example-vector-add:v42"
      resources:
        limits:
          gpu-vendor.example/example-gpu: 1 # requesting 1 GPU
```

The page uses a placeholder resource name; on a real cluster use the name your device plugin exposes. [55] The page does not say whether a GPU can be shared between Pods or requested as a fraction, so this lesson makes no claim about sharing.

## Mixed GPU types

If nodes carry different GPU types, label them and select with node selectors so a job that needs a particular accelerator lands on it. [55]

```bash
kubectl label nodes node1 accelerator=example-gpu-x100
kubectl label nodes node2 accelerator=other-gpu-k915
```

The `accelerator` key is only an example; any label key works. [55]

## Labels by detection

Node Feature Discovery (NFD) detects each node's hardware features and advertises them as labels. It can also add extended resources, annotations or node taints so that only Pods requesting specific features land on those nodes. A vendor or generic NFD plugin is needed to add GPU-related labels. [55]

The page's second example uses node affinity with an NFD label to require a GPU with more than a given amount of installed memory:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: "gpu.gpu-vendor.example/installed-memory"
          operator: Gt # (greater than)
          values: ["40535"]
```

[55]

## What this means for ML

Training and large-model serving usually want specific accelerators, so label or detect them and select deliberately. That also affects the cost conversation: a Pod that asks for any GPU may land on an expensive one, and a Pod without a selector can wait on a type you do not have. The page itself does not discuss cost, scheduling policy beyond labels and affinity, or monitoring GPU use. [55]

:::low-confidence
The Kubernetes page covers requesting and placing GPUs. It does not cover GPU sharing, utilisation monitoring or multi-node training, so those need other sources. [55]
:::

:::key-takeaways
- GPUs appear as a resource such as `nvidia.com/gpu` once the vendor driver and device plugin are installed by the administrator. [55]
- Specify GPUs in `limits`; requests, if given, must equal the limit. [55]
- Use node labels, selectors or NFD-based affinity to place Pods on the right GPU type. [55]
:::

:::glossary
- **Kubernetes**: software that runs containers across a group of machines.
- **Node**: one machine in a Kubernetes cluster.
- **Pod**: the smallest thing Kubernetes runs: one or more containers together.
- **Pending (Pod)**: accepted but not yet placed on a node.
- **GPU**: a graphics chip, much faster than a CPU at the parallel maths ML needs.
- **Device plugin**: an add-on that makes special hardware (GPUs) visible to Kubernetes.
- **Driver**: the software that lets the operating system use a piece of hardware.
- **Schedulable resource**: something Kubernetes can count and hand out, like CPU, memory or `nvidia.com/gpu`.
- **Requests / limits**: the amount of a resource reserved for a container / the most it may use.
- **Accelerator**: special hardware (like a GPU) that speeds up computation.
- **Label**: a key-value tag on a Kubernetes object.
- **Node selector**: a rule "only run on nodes with this label".
- **Node affinity**: a more flexible placement rule that can prefer or require certain node features.
- **NFD (Node Feature Discovery)**: a tool that detects hardware and labels nodes automatically.
- **Taint**: a mark on a node that keeps Pods away unless they say they accept it.
- **Extended resource**: a custom countable resource added to a node.
- **`kubectl`**: the command-line tool for Kubernetes.
:::
