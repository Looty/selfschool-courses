---
id: l30
title: "The node view: kubelet, containerd, crictl and nsenter"
quiz: quiz-01.yaml
resources: [../resources/lab6/lab6-run.sh]
sources: [72, 78, 79, 83]
---
After this lesson you can debug a Kubernetes node when `kubectl` is not enough: list pods and containers straight from the runtime, enter a pod's network namespace from the host, and read the node conditions and eviction thresholds the kubelet acts on.

## Who does what on a node

Kubernetes implements only part of its own network model. Setting up a pod's network namespace is the job of the container runtime behind the Container Runtime Interface (CRI); the pod network is a CNI plugin's job; Service traffic is handled by kube-proxy or a CNI's own proxy. [72] On the node that means three layers to look at when a pod misbehaves: the kubelet (decides what should run), the runtime (containerd, runs it), and the kernel networking the CNI plugin configured.

## crictl: the runtime's view

`crictl` is a command-line interface for CRI-compatible runtimes, meant for inspecting and debugging runtimes and applications on a node. [78] It reads its endpoint from `/etc/crictl.yaml` (`runtime-endpoint: unix:///var/run/containerd/containerd.sock` in the documentation's example); without one it tries a list of known endpoints, which costs time. [78] Everyday commands: `crictl pods` (pod sandboxes, filterable by `--name` and `--label`), `crictl ps -a` (all containers, including exited ones), `crictl images`, `crictl logs <id>` and `crictl exec -it <id> <cmd>`. [78]

From Lab 6, on a K3s node (K3s bundles crictl):

```text
$ crictl pods --name '^client$'
POD ID              CREATED             STATE               NAME                NAMESPACE
868072eda2f4a       17 seconds ago      Ready               client              default
$ crictl inspectp -o go-template --template '{{.info.pid}}' 868072eda2f4a...
671
```

`crictl` talks to the runtime directly, so it still answers when the API server is down, which is exactly when you need it. Use it to look and to read logs; the kubelet stays in charge of what runs.

## nsenter: stand inside the pod's network

Every pod has its own network namespace shared by its containers. [72] `nsenter` runs a program in another process's namespaces: `-t PID` picks the target, `-n` the network namespace, `-m` mount, `-p` PID. [83] With the sandbox PID from crictl, you get the pod's view of the network using the **node's** tools, even if the container image has no shell:

```text
$ nsenter -t 671 -n ip -o addr show eth0
eth0 10.42.0.5/24
$ nsenter -t 671 -n ip link show eth0
2: eth0@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 ...
```

`eth0@if8` says the other end of this veth pair is interface 8 on the node; lesson 31 follows it.

## Node conditions and eviction

The kubelet watches eviction signals and maps them to node conditions: [79]

| Condition | Signals |
| --- | --- |
| `MemoryPressure` | `memory.available` |
| `DiskPressure` | `nodefs.available`, `nodefs.inodesFree`, `imagefs.*`, `containerfs.*` |
| `PIDPressure` | `pid.available` |

Default hard thresholds on Linux are `memory.available<100Mi`, `nodefs.available<10%`, `imagefs.available<15%`, `nodefs.inodesFree<5%` and `imagefs.inodesFree<5%`. Change one, and the others become zero unless you set all of them or enable `MergeDefaultEvictionSettings`. [79] `memory.available` comes from cgroupfs, not `free -m`, and excludes inactive file cache. [79] Note `inodesFree`: a node can hit DiskPressure with free space if something creates millions of small files, the same failure you met with `df -i` in chapter 07.

Eviction is different from an OOM kill. If the kernel runs out of memory before the kubelet reclaims, the OOM killer acts, guided by the `oom_score_adj` the kubelet set per QoS class (-997 for Guaranteed, 1000 for BestEffort). An OOM-killed container restarts per its `restartPolicy`; an evicted pod does not come back on that node. [79]

## A node triage sequence

```bash
kubectl describe node <node>          # Conditions, Allocated resources, Events
crictl ps -a | grep -v Running        # exited or crash-looping containers
crictl logs <container-id>            # logs even if the API server is unhappy
nsenter -t <pid> -n ip addr / ss -tanp   # the pod's network from the host
```

:::key-takeaways
- The CRI runtime sets up pod network namespaces; CNI plugins build the pod network; kube-proxy handles Services. [72]
- `crictl pods`, `ps -a`, `logs`, `exec` and `inspectp` debug a node without the API server. [78]
- `nsenter -t PID -n` runs host tools inside a pod's network namespace. [83]
- MemoryPressure, DiskPressure and PIDPressure come from eviction signals with default hard thresholds. [79]
- Eviction (kubelet) and OOM kill (kernel) are different; QoS sets `oom_score_adj`. [79]
:::

:::glossary
- **kubelet**: the node agent that runs pods as the API server tells it to.
- **containerd**: the container runtime K3s and many clusters use.
- **CRI**: Container Runtime Interface, the API between the kubelet and the runtime.
- **crictl**: a CLI that talks to a CRI runtime directly.
- **Pod sandbox**: the runtime object that holds a pod's namespaces.
- **Network namespace**: a separate copy of the network stack (interfaces, routes, iptables) for a group of processes.
- **nsenter**: a tool that runs a command inside another process's namespaces.
- **Node condition**: a status flag such as DiskPressure that the kubelet reports.
:::
